"""Faz 2 BERTurk (dbmdz/bert-base-turkish-cased) ince ayar eğitim şablonu.

Bu betik, etik kurul onaylı ve PHQ-9 ≥ 10 ile etiketlenmiş Türkçe metin veri seti
hazır olduğunda GPU ortamında çalıştırılmak üzere tasarlanmıştır.

Öne çıkan bilimsel güvenceler:
    - Kişi bazlı gruplanmış tabakalı çapraz doğrulama (`StratifiedGroupKFold`): aynı
      katılımcının metinleri asla hem eğitim hem doğrulama katında bulunmaz.
    - Sınıf dengesizliği için ters sıklık ağırlıklı kayıp fonksiyonu (SMOTE yerine).
    - Kat dışı olasılıklar üzerinde sıcaklık/sigmoid kalibrasyonu, ROC-AUC, PR-AUC,
      Brier skoru ve %90 özgüllükte duyarlılık kaydı (TRIPOD+AI uyumlu).

Kullanım (GPU ortamında `torch` ve `transformers` kurulu iken):
    python scripts/train_berturk_template.py \
        --input data/turkish_phq9_texts.csv \
        --text-col text --label-col phq9_positive --group-col participant_id \
        --output-dir artifacts/berturk_cv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from mental_pulse.fusion import sensitivity_at_specificity

DEFAULT_MODEL_NAME = "dbmdz/bert-base-turkish-cased"


def validate_input_schema(
    df: pd.DataFrame, text_col: str, label_col: str, group_col: str
) -> None:
    """Girdi CSV şemasını ve temel veri bütünlüğünü doğrular."""
    missing = [c for c in (text_col, label_col, group_col) if c not in df.columns]
    if missing:
        raise ValueError(f"Eksik sütun(lar): {missing}")
    if df[label_col].dropna().nunique() != 2:
        raise ValueError("label_col tam olarak 2 sınıf (0/1) içermelidir.")
    if df[group_col].nunique() < 5:
        raise ValueError("StratifiedGroupKFold için en az 5 benzersiz katılımcı (group) gerekir.")


def run_training(args: argparse.Namespace) -> int:
    try:
        import torch
        from torch.utils.data import Dataset
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            EarlyStoppingCallback,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        print(
            "HATA: Bu şablon GPU ortamında `torch` ve `transformers` gerektirir.\n"
            "Kurulum: pip install torch transformers accelerate\n"
            f"Ayrıntı: {exc}",
            file=sys.stderr,
        )
        return 2

    df = pd.read_csv(args.input).dropna(subset=[args.text_col, args.label_col, args.group_col])
    validate_input_schema(df, args.text_col, args.label_col, args.group_col)

    texts = df[args.text_col].astype(str).tolist()
    labels = df[args.label_col].astype(int).to_numpy()
    groups = df[args.group_col].to_numpy()

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    class TextDataset(Dataset):
        def __init__(self, x_list: list[str], y_arr: np.ndarray):
            self.enc = tokenizer(
                x_list, truncation=True, padding=True, max_length=args.max_length
            )
            self.labels = y_arr.tolist()

        def __len__(self) -> int:
            return len(self.labels)

        def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
            item = {k: torch.tensor(v[idx]) for k, v in self.enc.items()}
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
            return item

    class WeightedTrainer(Trainer):
        def __init__(self, class_weights: torch.Tensor, **kwargs):
            super().__init__(**kwargs)
            self.class_weights = class_weights

        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            y_true = inputs.pop("labels")
            outputs = model(**inputs)
            loss_fn = torch.nn.CrossEntropyLoss(
                weight=self.class_weights.to(outputs.logits.device)
            )
            loss = loss_fn(outputs.logits, y_true)
            return (loss, outputs) if return_outputs else loss

    splitter = StratifiedGroupKFold(n_splits=args.splits, shuffle=True, random_state=args.seed)
    oof_probs = np.zeros(len(df), dtype=float)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for fold, (tr_idx, va_idx) in enumerate(splitter.split(df, labels, groups), start=1):
        assert set(groups[tr_idx]).isdisjoint(set(groups[va_idx]))
        tr_ds = TextDataset([texts[i] for i in tr_idx], labels[tr_idx])
        va_ds = TextDataset([texts[i] for i in va_idx], labels[va_idx])

        n_pos = max(1, int(labels[tr_idx].sum()))
        n_neg = max(1, int(len(tr_idx) - n_pos))
        weights = torch.tensor([len(tr_idx) / (2 * n_neg), len(tr_idx) / (2 * n_pos)], dtype=torch.float)

        model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2)
        t_args = TrainingArguments(
            output_dir=str(out_dir / f"fold_{fold}"),
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=args.lr,
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=args.batch_size,
            num_train_epochs=args.epochs,
            weight_decay=0.01,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            seed=args.seed + fold,
            report_to="none",
        )
        trainer = WeightedTrainer(
            class_weights=weights,
            model=model,
            args=t_args,
            train_dataset=tr_ds,
            eval_dataset=va_ds,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
        )
        trainer.train()
        logits = trainer.predict(va_ds).predictions
        probs = torch.softmax(torch.tensor(logits), dim=-1).numpy()[:, 1]
        oof_probs[va_idx] = probs

    summary = {
        "model_name": args.model_name,
        "n_samples": int(len(df)),
        "n_unique_participants": int(df[args.group_col].nunique()),
        "positive_rate": round(float(labels.mean()), 4),
        "oof_roc_auc": round(float(roc_auc_score(labels, oof_probs)), 4),
        "oof_pr_auc": round(float(average_precision_score(labels, oof_probs)), 4),
        "oof_brier_score": round(float(brier_score_loss(labels, oof_probs)), 4),
        "oof_sens_at_90_spec": round(sensitivity_at_specificity(labels, oof_probs, 0.90), 4),
    }
    (out_dir / "tripod_ai_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Faz 2 BERTurk kişi-bazlı CV ince ayar şablonu.")
    p.add_argument("--input", required=True, help="PHQ-9 etiketli Türkçe metin CSV yolu")
    p.add_argument("--text-col", default="text")
    p.add_argument("--label-col", default="phq9_positive")
    p.add_argument("--group-col", default="participant_id")
    p.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    p.add_argument("--output-dir", default="artifacts/berturk_cv")
    p.add_argument("--splits", type=int, default=5)
    p.add_argument("--epochs", type=int, default=4)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--seed", type=int, default=42)
    return p


if __name__ == "__main__":
    sys.exit(run_training(build_parser().parse_args()))
