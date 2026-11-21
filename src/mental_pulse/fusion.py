"""Faz 1–3 çok kipli (metin + demografi + pasif sensör) sızıntısız boru hattı ve Riley (2020) örneklem hesabı.

Kaynaklar:
    - Riley, R. D., Ensor, J., Snell, K. I. E., Harrell, F. E., Jr., Martin, G. P.,
      Reitsma, J. B., Moons, K. G. M., Collins, G., & van Smeden, M. (2020).
      Calculating the sample size required for developing a clinical prediction model.
      BMJ, 368, m441. https://doi.org/10.1136/bmj.m441
    - Collins, G. S., et al. (2024). TRIPOD+AI statement. BMJ, 385, e078378.
    - Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in
      machine-learning-based science. Patterns, 4(9), 100804.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .screening import extract_turkish_linguistic_features

LINGUISTIC_FEATURE_NAMES: tuple[str, ...] = (
    "word_count",
    "sentence_count",
    "avg_word_length",
    "first_person_singular_ratio",
    "absolutist_ratio",
    "negative_emotion_ratio",
    "positive_emotion_ratio",
    "somatic_sleep_ratio",
    "affect_balance",
    "question_mark_count",
    "exclamation_mark_count",
)


class TurkishPsycholinguisticTransformer(BaseEstimator, TransformerMixin):
    """Türkçe metin serisini scikit-learn uyumlu 11 psikolinguistik özelliğe dönüştürür."""

    def fit(self, X: Sequence[str], y: Any = None) -> "TurkishPsycholinguisticTransformer":
        return self

    def transform(self, X: Sequence[str]) -> np.ndarray:
        rows = []
        for text in X:
            feats = extract_turkish_linguistic_features("" if pd.isna(text) else str(text))
            d = feats.to_dict()
            rows.append([float(d[name]) for name in LINGUISTIC_FEATURE_NAMES])
        return np.asarray(rows, dtype=float)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        return np.asarray(LINGUISTIC_FEATURE_NAMES, dtype=object)


def build_multimodal_pipeline(
    text_col: str = "text",
    categorical_cols: Sequence[str] = (),
    numeric_cols: Sequence[str] = (),
    max_tfidf_features: int = 1500,
    calibrate: bool = False,
    random_state: int = 42,
) -> Pipeline:
    """Metin (TF-IDF + psikolinguistik) + demografi + pasif sensör sızıntısız boru hattı kurar."""
    text_branch = FeatureUnion(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=max_tfidf_features,
                    sublinear_tf=True,
                ),
            ),
            (
                "psycholing",
                Pipeline(
                    [
                        ("extract", TurkishPsycholinguisticTransformer()),
                        ("scale", StandardScaler()),
                    ]
                ),
            ),
        ]
    )

    transformers: list[tuple[str, Any, Any]] = [("text", text_branch, text_col)]
    if categorical_cols:
        transformers.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="most_frequent")),
                        ("oh", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                list(categorical_cols),
            )
        )
    if numeric_cols:
        transformers.append(
            (
                "num",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                list(numeric_cols),
            )
        )

    pre = ColumnTransformer(transformers=transformers, remainder="drop")
    base_clf = LogisticRegression(
        C=0.5, max_iter=2000, class_weight="balanced", random_state=random_state
    )
    clf: Any = (
        CalibratedClassifierCV(base_clf, method="sigmoid", cv=3) if calibrate else base_clf
    )
    return Pipeline([("pre", pre), ("clf", clf)])


def sensitivity_at_specificity(
    y_true: np.ndarray, y_prob: np.ndarray, target_specificity: float = 0.90
) -> float:
    """Sabit özgüllükte (varsayılan %90) elde edilen en yüksek duyarlılığı hesaplar."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    spec = 1.0 - fpr
    eligible = tpr[spec >= target_specificity]
    return float(eligible.max()) if len(eligible) > 0 else 0.0


def evaluate_grouped_multimodal(
    df: pd.DataFrame,
    target_col: str,
    group_col: str,
    text_col: str = "text",
    categorical_cols: Sequence[str] = (),
    numeric_cols: Sequence[str] = (),
    n_splits: int = 5,
    calibrate: bool = False,
    random_state: int = 42,
) -> dict[str, Any]:
    """Kişi bazlı gruplanmış (StratifiedGroupKFold) sızıntısız değerlendirme çalıştırır.

    Aynı `group_col` kimliğine (ör. `participant_id`) sahip kayıtlar asla hem eğitim hem test
    katında yer almaz.
    """
    y = df[target_col].astype(int).to_numpy()
    groups = df[group_col].to_numpy()
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    oof_prob = np.zeros(len(df), dtype=float)
    fold_metrics = []

    for fold_idx, (tr_idx, te_idx) in enumerate(splitter.split(df, y, groups), start=1):
        tr_groups = set(groups[tr_idx])
        te_groups = set(groups[te_idx])
        assert tr_groups.isdisjoint(te_groups), "Kişi bazlı grup sızıntısı tespit edildi!"

        pipe = build_multimodal_pipeline(
            text_col=text_col,
            categorical_cols=categorical_cols,
            numeric_cols=numeric_cols,
            calibrate=calibrate,
            random_state=random_state + fold_idx,
        )
        pipe.fit(df.iloc[tr_idx], y[tr_idx])
        probs = pipe.predict_proba(df.iloc[te_idx])[:, 1]
        oof_prob[te_idx] = probs
        preds = (probs >= 0.5).astype(int)

        fold_metrics.append(
            {
                "fold": fold_idx,
                "n_test": int(len(te_idx)),
                "roc_auc": float(roc_auc_score(y[te_idx], probs)),
                "pr_auc": float(average_precision_score(y[te_idx], probs)),
                "balanced_accuracy": float(balanced_accuracy_score(y[te_idx], preds)),
                "brier_score": float(brier_score_loss(y[te_idx], probs)),
                "sens_at_90_spec": sensitivity_at_specificity(y[te_idx], probs, 0.90),
            }
        )

    folds_df = pd.DataFrame(fold_metrics)
    return {
        "n_samples": int(len(df)),
        "n_unique_groups": int(len(np.unique(groups))),
        "positive_rate": round(float(y.mean()), 4),
        "oof_roc_auc": round(float(roc_auc_score(y, oof_prob)), 4),
        "oof_pr_auc": round(float(average_precision_score(y, oof_prob)), 4),
        "oof_brier_score": round(float(brier_score_loss(y, oof_prob)), 4),
        "oof_sens_at_90_spec": round(sensitivity_at_specificity(y, oof_prob, 0.90), 4),
        "fold_summary": folds_df,
    }


@dataclass(frozen=True)
class RileySampleSizeResult:
    """Riley vd. (2020, BMJ) ikili klinik tahmin modeli örneklem büyüklüğü sonucu."""

    prevalence: float
    n_parameters: int
    anticipated_r2_cs: float
    max_r2_cs: float
    n_criterion_1_prevalence: int
    n_criterion_2_shrinkage: int
    n_criterion_3_optimism: int
    recommended_min_n: int
    expected_events: float
    events_per_parameter: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def sample_size_riley_binary(
    prevalence: float,
    n_parameters: int,
    anticipated_r2_cs: float | None = None,
    shrinkage_target: float = 0.90,
    margin_of_error: float = 0.05,
    optimism_nagelkerke: float = 0.05,
) -> RileySampleSizeResult:
    """Riley vd. (2020, BMJ 368:m441) ölçütleriyle ikili sonuç için minimum örneklem hesaplar.

    Ölçütler:
        1) Genel olay oranını ±`margin_of_error` (%95 GA) hassasiyetle tahmin (B1)
        2) Beklenen küçülme faktörünü (shrinkage) ≥ `shrinkage_target` tutma (B3)
        3) Nagelkerke R² iyimserliğini ≤ `optimism_nagelkerke` sınırlama (B4)
    """
    if not (0.0 < prevalence < 1.0):
        raise ValueError("prevalence (0, 1) aralığında olmalıdır.")
    if n_parameters < 1:
        raise ValueError("n_parameters en az 1 olmalıdır.")
    if not (0.0 < shrinkage_target < 1.0):
        raise ValueError("shrinkage_target (0, 1) aralığında olmalıdır.")

    # Null model log-olabilirliği ve maksimum Cox-Snell R^2 (Riley 2020, Ek S5)
    ln_l_null = prevalence * math.log(prevalence) + (1.0 - prevalence) * math.log(1.0 - prevalence)
    max_r2_cs = 1.0 - math.exp(2.0 * ln_l_null)

    # Belirtilmezse Riley (2020) konservatif önerisi: max(R2_cs)'in %15'i
    r2_cs = (0.15 * max_r2_cs) if anticipated_r2_cs is None else float(anticipated_r2_cs)
    if not (0.0 < r2_cs < max_r2_cs):
        raise ValueError(
            f"anticipated_r2_cs (0, {max_r2_cs:.4f}) aralığında olmalıdır; alınan: {r2_cs}"
        )

    # Ölçüt 1: Prevalans tahmini (z = 1.96)
    n1 = math.ceil((1.96 / margin_of_error) ** 2 * prevalence * (1.0 - prevalence))

    # Ölçüt 2: Küçülme faktörü S (Riley 2020, Şekil 3)
    denom_s = (shrinkage_target - 1.0) * math.log(1.0 - (r2_cs / shrinkage_target))
    n2 = math.ceil(n_parameters / denom_s)

    # Ölçüt 3: Nagelkerke R^2 iyimserliği ≤ delta (Riley 2020, Şekil 5)
    s_opt = r2_cs / (r2_cs + optimism_nagelkerke * max_r2_cs)
    denom_opt = (s_opt - 1.0) * math.log(1.0 - (r2_cs / s_opt))
    n3 = math.ceil(n_parameters / denom_opt)

    min_n = max(n1, n2, n3)
    expected_events = min_n * prevalence
    epp = expected_events / n_parameters

    return RileySampleSizeResult(
        prevalence=round(prevalence, 4),
        n_parameters=int(n_parameters),
        anticipated_r2_cs=round(r2_cs, 4),
        max_r2_cs=round(max_r2_cs, 4),
        n_criterion_1_prevalence=int(n1),
        n_criterion_2_shrinkage=int(n2),
        n_criterion_3_optimism=int(n3),
        recommended_min_n=int(min_n),
        expected_events=round(expected_events, 1),
        events_per_parameter=round(epp, 2),
    )
