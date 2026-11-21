"""Mental Pulse komut satırı arayüzü (CLI)."""

from __future__ import annotations

import argparse
import json
import sys

from .data import load_rhmcd20, run_full_audit
from .fusion import sample_size_riley_binary
from .modeling import evaluate_target, reproduce_original_bug, subgroup_fairness_report
from .screening import extract_turkish_linguistic_features, score_gad7, score_phq9
from .stats import pairwise_cramers_v, run_literature_hypotheses
from .temporal import compute_erde, compute_f_latency


def _cmd_audit(args: argparse.Namespace) -> int:
    df = load_rhmcd20(args.data)
    audit = run_full_audit(df)
    _, pairs = pairwise_cramers_v(df)
    hyps = run_literature_hypotheses(df)

    print("=== RHMCD-20 VERİ KALİTESİ DENETİMİ ===")
    print(
        f"Boyut: {audit['n_rows']}x{audit['n_cols']} | "
        f"Eksik: {audit['missing_cells']} | Tekrarlı: {audit['duplicate_rows']} | "
        f"Dokümantasyon uyumsuzluğu: {audit['doc_mismatches']}/13 | "
        f"Tekdüzeden farksız sütun: {audit['uniform_columns']}/13"
    )
    print("\n--- Mantıksal Tutarlılık ---")
    print(audit["plausibility"].to_string(index=False))
    print("\n--- En Yüksek 5 Cramér's V Çifti (78 çift içinde) ---")
    print(
        pairs[["var_a_tr", "var_b_tr", "cramers_v", "p_value", "q_fdr"]]
        .head(5)
        .round(4)
        .to_string(index=False)
    )
    print(f"FDR q<0.05 anlamlı çift sayısı: {int((pairs['q_fdr'] < 0.05).sum())}")
    print("\n--- Literatür Hipotez Testleri ---")
    print(
        hyps[["id", "var_a", "var_b", "cramers_v", "p_value", "q_fdr", "supported_fdr_05"]]
        .to_string(index=False)
    )
    return 0


def _cmd_benchmark(args: argparse.Namespace) -> int:
    df = load_rhmcd20(args.data)
    report = evaluate_target(
        df,
        target=args.target,
        binary_positive=args.binary_positive,
        n_splits=args.splits,
        n_repeats=args.repeats,
        n_permutations=args.permutations,
    )
    print(f"=== SIZINTISIZ MODEL KIYASLAMASI | Hedef: {report.target} ===")
    print(f"Sınıf dağılımı: {report.class_counts}")
    print(report.cv_summary.to_string(index=False))
    print(
        f"\nPermütasyon testi (LogReg, dengeli doğruluk): "
        f"gözlenen={report.permutation_score:.4f}, "
        f"şans ort.={report.permutation_null_mean:.4f}, "
        f"p={report.permutation_p_value:.4f}"
    )

    if args.fairness:
        fair = subgroup_fairness_report(
            df, target=args.target, positive_label=args.binary_positive or "Yes", group_col="Gender"
        )
        print("\n--- Alt Grup Adalet ve Kalibrasyon (Cinsiyet) ---")
        print(fair.to_string(index=False))

    if args.repro_bug:
        df_tr = load_rhmcd20(turkish=True)
        print("\n--- Orijinal analiz.ipynb H1 Hatası Yeniden Üretimi ---")
        print(reproduce_original_bug(df_tr).to_string(index=False))
    return 0


def _cmd_features(args: argparse.Namespace) -> int:
    feats = extract_turkish_linguistic_features(args.text)
    print(json.dumps(feats.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_screen(args: argparse.Namespace) -> int:
    vals = [int(x.strip()) for x in args.scores.split(",")]
    if args.scale == "phq9":
        res = score_phq9(vals)
        print(json.dumps(res.__dict__, ensure_ascii=False, indent=2))
    else:
        res = score_gad7(vals)
        print(json.dumps(res.__dict__, ensure_ascii=False, indent=2))
    return 0


def _cmd_sample_size(args: argparse.Namespace) -> int:
    res = sample_size_riley_binary(
        prevalence=args.prevalence,
        n_parameters=args.parameters,
        anticipated_r2_cs=args.r2_cs,
        shrinkage_target=args.shrinkage,
    )
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))
    return 0


def _cmd_erde(args: argparse.Namespace) -> int:
    yt = [int(x.strip()) for x in args.y_true.split(",")]
    yp = [int(x.strip()) for x in args.y_pred.split(",")]
    ks = [int(x.strip()) for x in args.delays.split(",")]
    out = {
        "erde_5": round(compute_erde(yt, yp, ks, o=5), 4),
        "erde_50": round(compute_erde(yt, yp, ks, o=50), 4),
        **compute_f_latency(yt, yp, ks),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mental-pulse",
        description="Mental Pulse: veri kalitesi denetimi, sızıntısız modelleme, örneklem hesabı ve tarama araçları.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="RHMCD-20 veri kalitesi ve ilişki denetimini çalıştırır.")
    p_audit.add_argument("--data", default=None, help="CSV dosya yolu (varsayılan: mentalHealth/data.csv)")
    p_audit.set_defaults(func=_cmd_audit)

    p_bench = sub.add_parser("benchmark", help="Sızıntısız çapraz doğrulama ve permütasyon testi çalıştırır.")
    p_bench.add_argument("--data", default=None, help="CSV dosya yolu")
    p_bench.add_argument("--target", default="Social_Weakness", help="Hedef sütun adı")
    p_bench.add_argument("--binary-positive", default=None, help="İkili hedef için pozitif sınıf (ör. Yes)")
    p_bench.add_argument("--splits", type=int, default=5)
    p_bench.add_argument("--repeats", type=int, default=3)
    p_bench.add_argument("--permutations", type=int, default=100)
    p_bench.add_argument("--fairness", action="store_true", help="Alt grup adalet tablosunu yazdırır")
    p_bench.add_argument("--repro-bug", action="store_true", help="Orijinal H1 hatasını yeniden üretir")
    p_bench.set_defaults(func=_cmd_benchmark)

    p_feat = sub.add_parser("features", help="Türkçe metinden psikolinguistik özellikleri çıkarır.")
    p_feat.add_argument("text", help="Analiz edilecek Türkçe metin")
    p_feat.set_defaults(func=_cmd_features)

    p_scr = sub.add_parser("screen", help="PHQ-9 veya GAD-7 ölçek puanlaması (tanı aracı değildir).")
    p_scr.add_argument("--scale", choices=["phq9", "gad7"], required=True)
    p_scr.add_argument("--scores", required=True, help="Virgülle ayrılmış 0-3 puanlar (ör. 1,2,1,2,1,1,1,0,0)")
    p_scr.set_defaults(func=_cmd_screen)

    p_ss = sub.add_parser("sample-size", help="Riley vd. (2020, BMJ) minimum örneklem büyüklüğünü hesaplar.")
    p_ss.add_argument("--prevalence", type=float, required=True, help="Beklenen pozitif sınıf oranı (ör. 0.064)")
    p_ss.add_argument("--parameters", type=int, required=True, help="Aday öngörücü parametre sayısı (ör. 15)")
    p_ss.add_argument("--r2-cs", type=float, default=None, help="Beklenen Cox-Snell R² (boş bırakılırsa konservatif %15)")
    p_ss.add_argument("--shrinkage", type=float, default=0.90, help="Hedef küçülme faktörü (varsayılan 0.90)")
    p_ss.set_defaults(func=_cmd_sample_size)

    p_erde = sub.add_parser("erde", help="CLEF eRisk ERDE_5, ERDE_50 ve F_latency metriklerini hesaplar.")
    p_erde.add_argument("--y-true", required=True, help="Gerçek etiketler (ör. 1,1,0,0)")
    p_erde.add_argument("--y-pred", required=True, help="Tahminler (ör. 1,1,0,1)")
    p_erde.add_argument("--delays", required=True, help="Karar gecikmeleri k (ör. 3,25,10,5)")
    p_erde.set_defaults(func=_cmd_erde)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
