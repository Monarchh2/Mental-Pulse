"""Kategorik değişkenler için istatistiksel ilişki ve hipotez testi araçları.

Orijinal not defterinde kategorik sütunlar alfabetik LabelEncoder ile sayısala
çevrilip Pearson korelasyonu hesaplanmıştı. Bu modül bunun yerine Bergsma (2013)
yanlılık düzeltmeli Cramér's V ölçüsünü ve Benjamini–Hochberg (1995) çoklu
karşılaştırma (FDR) düzeltmesini uygular.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, false_discovery_control

from .data import TR_LABELS


def cramers_v_bias_corrected(x: pd.Series, y: pd.Series) -> tuple[float, float, float, int]:
    """Bergsma (2013) yanlılık düzeltmeli Cramér's V ve ki-kare istatistiklerini hesaplar.

    Returns:
        (v_corrected, p_value, chi2_stat, dof)
    """
    ct = pd.crosstab(x, y)
    chi2, p_value, dof, _ = chi2_contingency(ct, correction=False)
    n = float(ct.values.sum())
    r, k = ct.shape
    if n <= 1 or min(r, k) <= 1:
        return 0.0, float(p_value), float(chi2), int(dof)

    phi2 = chi2 / n
    phi2_corr = max(0.0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    r_corr = r - ((r - 1) ** 2) / (n - 1)
    k_corr = k - ((k - 1) ** 2) / (n - 1)
    denom = min(k_corr - 1.0, r_corr - 1.0)
    v_corr = float(np.sqrt(phi2_corr / denom)) if denom > 0 else 0.0
    return v_corr, float(p_value), float(chi2), int(dof)


def pairwise_cramers_v(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tüm değişken çiftleri için Cramér's V matrisi ve BH-FDR düzeltmeli tablo döndürür."""
    cols = list(df.columns)
    matrix = pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols, dtype=float)
    records = []

    for i, col_a in enumerate(cols):
        for j in range(i + 1, len(cols)):
            col_b = cols[j]
            v, p_val, chi2, dof = cramers_v_bias_corrected(df[col_a], df[col_b])
            matrix.iloc[i, j] = matrix.iloc[j, i] = v
            records.append(
                {
                    "var_a": col_a,
                    "var_b": col_b,
                    "var_a_tr": TR_LABELS.get(col_a, col_a),
                    "var_b_tr": TR_LABELS.get(col_b, col_b),
                    "cramers_v": v,
                    "chi2": chi2,
                    "dof": dof,
                    "p_value": p_val,
                }
            )

    pairs = pd.DataFrame(records)
    if not pairs.empty:
        pairs["q_fdr"] = false_discovery_control(pairs["p_value"].to_numpy(), method="bh")
        pairs = pairs.sort_values("p_value", ascending=True).reset_index(drop=True)
    return matrix, pairs


LITERATURE_HYPOTHESES: list[tuple[str, str, str, str]] = [
    (
        "H1",
        "Gender",
        "Growing_Stress",
        "Kadınlarda stres/depresif belirti daha yüksektir (Salk vd., 2017; Yıldız vd., 2024)",
    ),
    (
        "H2",
        "Days_Indoors",
        "Growing_Stress",
        "Uzun karantina süresi stresle ilişkilidir (Brooks vd., 2020; Prati & Mancini, 2021)",
    ),
    (
        "H3",
        "Mental_Health_History",
        "Mood_Swings",
        "Aile ruh sağlığı öyküsü duygudurum dalgalanmalarıyla ilişkilidir",
    ),
    (
        "H4",
        "Changes_Habits",
        "Weight_Change",
        "Yeme/uyku alışkanlığı değişimi kilo değişimiyle yakından ilişkilidir (DSM-5 belirti kümesi)",
    ),
    (
        "H5",
        "Growing_Stress",
        "Coping_Struggles",
        "Artan stres başa çıkma güçlüğüyle ilişkilidir",
    ),
    (
        "H6",
        "Occupation",
        "Gender",
        "Meslek dağılımı cinsiyete göre farklılaşır (ör. Housewife kategorisi)",
    ),
]


def run_literature_hypotheses(df: pd.DataFrame) -> pd.DataFrame:
    """Literatürden türetilen temel ilişkileri RHMCD-20 üzerinde sınar."""
    rows = []
    for hid, a, b, rationale in LITERATURE_HYPOTHESES:
        v, p_val, chi2, dof = cramers_v_bias_corrected(df[a], df[b])
        rows.append(
            {
                "id": hid,
                "var_a": a,
                "var_b": b,
                "rationale": rationale,
                "chi2": round(chi2, 3),
                "dof": dof,
                "cramers_v": round(v, 4),
                "p_value": round(p_val, 4),
            }
        )
    out = pd.DataFrame(rows)
    out["q_fdr"] = np.round(false_discovery_control(out["p_value"].to_numpy(), method="bh"), 4)
    out["supported_fdr_05"] = out["q_fdr"] < 0.05
    return out
