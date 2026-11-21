"""RHMCD-20 veri seti yükleme, şema tanımları ve veri kalitesi denetimi.

Veri kaynağı:
    Salehin, I., & Amin, N. (2023). The RHMCD-20 datasets for Depression and
    Mental Health Data Analysis with Machine Learning. Mendeley Data, V2.
    DOI: 10.17632/pxjmjyfdh2.2 (CC BY 4.0)
    Amin, N., Salehin, I., Baten, M. A., & Al Noman, R. (2024). Data in Brief,
    54, 110376. DOI: 10.1016/j.dib.2024.110376
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import chisquare

# Veri makalesindeki (Amin vd., 2024, Tablo 2) belgelenen kategoriler
DOCUMENTED_CATEGORIES: dict[str, set[str]] = {
    "Age": {"16-20", "20-25", "25-30", "30-Above"},
    "Gender": {"Female", "Male"},
    "Occupation": {"Business", "Corporate", "Housewife", "Others", "Student"},
    "Days_Indoors": {
        "Go out Every day",
        "1-14 days",
        "15-30 days",
        "31-60 days",
        "More than 2 months",
    },
    "Growing_Stress": {"No", "Maybe", "Yes"},
    "Quarantine_Frustrations": {"No", "Maybe", "Yes"},
    "Changes_Habits": {"No", "Maybe", "Yes"},
    "Mental_Health_History": {"No", "Yes"},
    "Weight_Change": {"No", "Maybe", "Yes"},
    "Mood_Swings": {"Low", "Medium", "High"},
    "Coping_Struggles": {"No", "Maybe", "Yes"},
    "Work_Interest": {"No", "Yes"},
    "Social_Weakness": {"No", "Yes"},
}

# Sıralı değişkenler için doğal anlam sırası (LabelEncoder alfabetik hatasını önler)
ORDINAL_ORDERS: dict[str, list[str]] = {
    "Age": ["16-20", "20-25", "25-30", "30-Above"],
    "Days_Indoors": [
        "Go out Every day",
        "1-14 days",
        "15-30 days",
        "31-60 days",
        "More than 2 months",
    ],
    "Mood_Swings": ["Low", "Medium", "High"],
    "Coping_Struggles": ["No", "Yes"],
    "Growing_Stress": ["No", "Maybe", "Yes"],
    "Quarantine_Frustrations": ["No", "Maybe", "Yes"],
    "Changes_Habits": ["No", "Maybe", "Yes"],
    "Mental_Health_History": ["No", "Maybe", "Yes"],
    "Weight_Change": ["No", "Maybe", "Yes"],
    "Work_Interest": ["No", "Maybe", "Yes"],
    "Social_Weakness": ["No", "Maybe", "Yes"],
}

NOMINAL_COLUMNS: list[str] = ["Gender", "Occupation"]

# Düzeltilmiş Türkçe sütun etiketleri (raporlama için)
TR_LABELS: dict[str, str] = {
    "Age": "Yaş",
    "Gender": "Cinsiyet",
    "Occupation": "Meslek",
    "Days_Indoors": "Evde Kalınan Gün",
    "Growing_Stress": "Artan Stres",
    "Quarantine_Frustrations": "Karantina Hayal Kırıklığı",
    "Changes_Habits": "Alışkanlık Değişimi",
    "Mental_Health_History": "Aile Ruh Sağlığı Öyküsü",
    "Weight_Change": "Kilo Değişimi",
    "Mood_Swings": "Ruh Hâli Değişimleri",
    "Coping_Struggles": "Başa Çıkma Güçlüğü",
    "Work_Interest": "İşe İlgi Kaybı",
    "Social_Weakness": "Sosyal Zayıflık",
}


def default_data_path(turkish: bool = False) -> Path:
    """Depodaki varsayılan CSV yolunu döndürür."""
    repo_root = Path(__file__).resolve().parents[2]
    filename = "dataTR.csv" if turkish else "data.csv"
    return repo_root / "mentalHealth" / filename


def load_rhmcd20(path: str | Path | None = None, turkish: bool = False) -> pd.DataFrame:
    """RHMCD-20 veri setini yükler.

    Analizlerde çeviri hatalarından kaçınmak için İngilizce sürüm (`turkish=False`)
    kullanılması önerilir.
    """
    csv_path = Path(path) if path is not None else default_data_path(turkish=turkish)
    if not csv_path.exists():
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {csv_path}")
    return pd.read_csv(csv_path)


def check_documentation_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """CSV'de gözlenen kategorileri Amin vd. (2024, Tablo 2) ile karşılaştırır."""
    rows = []
    for col, expected in DOCUMENTED_CATEGORIES.items():
        if col not in df.columns:
            rows.append(
                {
                    "column": col,
                    "documented": sorted(expected),
                    "observed": [],
                    "consistent": False,
                }
            )
            continue
        observed = set(df[col].dropna().unique())
        rows.append(
            {
                "column": col,
                "documented": sorted(expected),
                "observed": sorted(observed),
                "consistent": observed == expected,
            }
        )
    return pd.DataFrame(rows)


def check_plausibility(df: pd.DataFrame) -> pd.DataFrame:
    """Demografik/mantıksal tutarlılık kontrollerini çalıştırır."""
    checks = [
        (
            "male_housewife",
            "Cinsiyet = Male ve Meslek = Housewife",
            int(((df["Gender"] == "Male") & (df["Occupation"] == "Housewife")).sum()),
        ),
        (
            "teen_corporate",
            "Yaş = 16-20 ve Meslek = Corporate",
            int(((df["Age"] == "16-20") & (df["Occupation"] == "Corporate")).sum()),
        ),
        (
            "teen_business",
            "Yaş = 16-20 ve Meslek = Business",
            int(((df["Age"] == "16-20") & (df["Occupation"] == "Business")).sum()),
        ),
        (
            "over30_student",
            "Yaş = 30-Above ve Meslek = Student",
            int(((df["Age"] == "30-Above") & (df["Occupation"] == "Student")).sum()),
        ),
    ]
    total = len(df)
    return pd.DataFrame(
        [
            {
                "check_id": cid,
                "description": desc,
                "count": cnt,
                "share_pct": round(100.0 * cnt / total, 2) if total else 0.0,
            }
            for cid, desc, cnt in checks
        ]
    )


def check_uniformity(df: pd.DataFrame) -> pd.DataFrame:
    """Her sütun için 'kategoriler eşit olasılıklı' ki-kare uyum iyiliği testi."""
    rows = []
    for col in df.columns:
        vc = df[col].value_counts()
        stat, pval = chisquare(vc.values)
        rows.append(
            {
                "column": col,
                "label_tr": TR_LABELS.get(col, col),
                "n_categories": int(len(vc)),
                "top_category": str(vc.index[0]),
                "top_share": round(float(vc.iloc[0] / vc.sum()), 4),
                "chi2": round(float(stat), 3),
                "p_value": round(float(pval), 4),
                "indistinguishable_from_uniform": bool(pval >= 0.05),
            }
        )
    return pd.DataFrame(rows)


def run_full_audit(df: pd.DataFrame) -> dict[str, Any]:
    """Tam veri kalitesi denetimi döndürür."""
    doc_df = check_documentation_consistency(df)
    plaus_df = check_plausibility(df)
    unif_df = check_uniformity(df)
    return {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "doc_mismatches": int((~doc_df["consistent"]).sum()),
        "uniform_columns": int(unif_df["indistinguishable_from_uniform"].sum()),
        "documentation_consistency": doc_df,
        "plausibility": plaus_df,
        "uniformity": unif_df,
    }
