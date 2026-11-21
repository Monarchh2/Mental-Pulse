"""Veri kalitesi denetimi ve istatistiksel ilişki testleri."""

import numpy as np
import pandas as pd

from mental_pulse.data import (
    check_documentation_consistency,
    check_plausibility,
    check_uniformity,
    load_rhmcd20,
    run_full_audit,
)
from mental_pulse.stats import (
    cramers_v_bias_corrected,
    pairwise_cramers_v,
    run_literature_hypotheses,
)


def test_rhmcd20_audit_reproduces_key_findings():
    df = load_rhmcd20()
    audit = run_full_audit(df)

    assert audit["n_rows"] == 824
    assert audit["n_cols"] == 13
    assert audit["missing_cells"] == 0
    assert audit["duplicate_rows"] == 0
    assert audit["doc_mismatches"] == 4
    assert audit["uniform_columns"] == 13

    plaus = check_plausibility(df).set_index("check_id")
    assert int(plaus.loc["male_housewife", "count"]) == 89
    assert int(plaus.loc["teen_corporate", "count"]) == 46


def test_documentation_consistency_flags_expected_columns():
    df = load_rhmcd20()
    doc = check_documentation_consistency(df).set_index("column")
    mismatched = set(doc.index[~doc["consistent"]])
    assert mismatched == {
        "Mental_Health_History",
        "Coping_Struggles",
        "Work_Interest",
        "Social_Weakness",
    }


def test_uniformity_table_structure():
    df = load_rhmcd20()
    unif = check_uniformity(df)
    assert len(unif) == 13
    assert (unif["p_value"] >= 0.05).all()


def test_cramers_v_bounds_and_perfect_association():
    s = pd.Series(["A", "B", "C"] * 40)
    v_perfect, p_val, _, _ = cramers_v_bias_corrected(s, s)
    assert 0.95 < v_perfect <= 1.0
    assert p_val < 1e-10

    rng = np.random.default_rng(42)
    a = pd.Series(rng.choice(["X", "Y", "Z"], size=600))
    b = pd.Series(rng.choice(["P", "Q", "R"], size=600))
    v_indep, _, _, _ = cramers_v_bias_corrected(a, b)
    assert 0.0 <= v_indep < 0.1


def test_pairwise_cramers_v_has_no_fdr_significant_pairs_in_rhmcd20():
    df = load_rhmcd20()
    mat, pairs = pairwise_cramers_v(df)
    assert mat.shape == (13, 13)
    assert len(pairs) == 78
    assert pairs["cramers_v"].max() < 0.10
    assert int((pairs["q_fdr"] < 0.05).sum()) == 0


def test_literature_hypotheses_all_unsupported_in_rhmcd20():
    df = load_rhmcd20()
    hyps = run_literature_hypotheses(df)
    assert len(hyps) == 6
    assert not hyps["supported_fdr_05"].any()
