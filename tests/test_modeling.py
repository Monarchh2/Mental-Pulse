"""Sızıntısız modelleme, permütasyon testi, alt grup adaleti ve hata yeniden üretimi testleri."""

from mental_pulse.data import load_rhmcd20
from mental_pulse.modeling import (
    evaluate_target,
    reproduce_original_bug,
    subgroup_fairness_report,
)


def test_evaluate_target_confirms_chance_level_performance():
    df = load_rhmcd20()
    report = evaluate_target(
        df,
        target="Social_Weakness",
        n_splits=5,
        n_repeats=2,
        n_permutations=30,
        random_state=42,
    )
    assert report.target == "Social_Weakness"
    assert not report.binary
    assert len(report.cv_summary) == 7
    assert report.cv_summary["roc_auc_mean"].max() < 0.56
    assert report.permutation_p_value > 0.10


def test_subgroup_fairness_report_covers_all_groups():
    df = load_rhmcd20()
    fair = subgroup_fairness_report(df, target="Social_Weakness", group_col="Gender")
    assert set(fair["subgroup"]) == {"Female", "Male"}
    assert int(fair["n"].sum()) == len(df)
    assert (fair["brier_score"] > 0).all()


def test_reproduce_original_bug_matches_notebook_numbers():
    df_tr = load_rhmcd20(turkish=True)
    cmp = reproduce_original_bug(df_tr).set_index("model")
    # Orijinal analiz.ipynb hücre 23 çıktılarıyla birebir deterministik modeller
    assert abs(cmp.loc["LogisticRegression", "male_acc_buggy_trained_on_female"] - 0.3419) < 0.002
    assert abs(cmp.loc["SVC", "male_acc_buggy_trained_on_female"] - 0.3675) < 0.002
    assert abs(cmp.loc["kNN", "male_acc_buggy_trained_on_female"] - 0.4444) < 0.002
    # Düzeltilmiş erkek modelleri farklı (daha düşük) sonuç verir
    assert (
        cmp.loc["kNN", "male_acc_fixed"]
        != cmp.loc["kNN", "male_acc_buggy_trained_on_female"]
    )
