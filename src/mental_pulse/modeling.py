"""Sızıntısız modelleme, çapraz doğrulama, permütasyon testi ve alt grup adalet analizi.

Tasarım ilkeleri:
    - Kapoor & Narayanan (2023): tüm ön işleme adımları yalnızca eğitim katında fit edilir.
    - TRIPOD+AI (Collins vd., 2024): taban çizgileri, ayrım (ROC-AUC), kalibrasyon (Brier)
      ve alt grup adalet (fairness) metrikleri birlikte raporlanır.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
    permutation_test_score,
    train_test_split,
)
from sklearn.naive_bayes import CategoricalNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.svm import SVC

from .data import NOMINAL_COLUMNS, ORDINAL_ORDERS


@dataclass
class EvaluationReport:
    """Bir hedef değişken için çapraz doğrulama ve permütasyon testi çıktısı."""

    target: str
    binary: bool
    class_counts: dict[Any, int]
    cv_summary: pd.DataFrame
    permutation_score: float
    permutation_null_mean: float
    permutation_p_value: float
    permutation_scores: np.ndarray


def build_candidate_models(
    feature_columns: list[str], random_state: int = 42
) -> dict[str, Pipeline]:
    """Sızıntısız ön işleme + model boru hatlarını (Pipeline) oluşturur."""
    ord_cols = [c for c in feature_columns if c in ORDINAL_ORDERS]
    nom_cols = [c for c in feature_columns if c in NOMINAL_COLUMNS]

    onehot = ColumnTransformer(
        [("oh", OneHotEncoder(handle_unknown="ignore"), feature_columns)]
    )
    ordinal_plus_nom = ColumnTransformer(
        [
            ("ord", OrdinalEncoder(categories=[ORDINAL_ORDERS[c] for c in ord_cols]), ord_cols),
            ("oh", OneHotEncoder(handle_unknown="ignore"), nom_cols),
        ]
    )
    cat_encoder = ColumnTransformer(
        [
            (
                "ord",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                feature_columns,
            )
        ]
    )

    return {
        "Dummy (most_frequent)": Pipeline(
            [("pre", onehot), ("clf", DummyClassifier(strategy="most_frequent"))]
        ),
        "Dummy (stratified)": Pipeline(
            [
                ("pre", onehot),
                ("clf", DummyClassifier(strategy="stratified", random_state=random_state)),
            ]
        ),
        "LogisticRegression (L2)": Pipeline(
            [("pre", onehot), ("clf", LogisticRegression(C=0.1, max_iter=2000))]
        ),
        "CategoricalNB": Pipeline([("pre", cat_encoder), ("clf", CategoricalNB())]),
        "RandomForest": Pipeline(
            [
                ("pre", onehot),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=200,
                        min_samples_leaf=5,
                        random_state=random_state,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "HistGradientBoosting": Pipeline(
            [
                ("pre", ordinal_plus_nom),
                (
                    "clf",
                    HistGradientBoostingClassifier(
                        max_depth=3, learning_rate=0.05, random_state=random_state
                    ),
                ),
            ]
        ),
        "kNN (k=15)": Pipeline([("pre", onehot), ("clf", KNeighborsClassifier(n_neighbors=15))]),
    }


def evaluate_target(
    df: pd.DataFrame,
    target: str = "Social_Weakness",
    binary_positive: str | None = None,
    n_splits: int = 5,
    n_repeats: int = 3,
    n_permutations: int = 100,
    random_state: int = 42,
) -> EvaluationReport:
    """Belirtilen hedef için tekrarlı tabakalı CV ve permütasyon testi çalıştırır."""
    X = df.drop(columns=[target])
    if binary_positive is not None:
        y = (df[target] == binary_positive).astype(int)
        binary = True
    else:
        y = df[target].copy()
        binary = y.nunique() == 2

    models = build_candidate_models(list(X.columns), random_state=random_state)
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    scoring = {
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "f1_macro": "f1_macro",
        "roc_auc": "roc_auc" if binary else "roc_auc_ovr",
    }

    rows = []
    for name, pipe in models.items():
        res = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        row: dict[str, Any] = {"model": name}
        for metric in scoring:
            vals = res[f"test_{metric}"]
            row[f"{metric}_mean"] = round(float(vals.mean()), 4)
            row[f"{metric}_std"] = round(float(vals.std()), 4)
        rows.append(row)

    lr_pipe = models["LogisticRegression (L2)"]
    perm_cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    obs_score, perm_scores, p_val = permutation_test_score(
        lr_pipe,
        X,
        y,
        cv=perm_cv,
        scoring="balanced_accuracy",
        n_permutations=n_permutations,
        n_jobs=-1,
        random_state=random_state,
    )

    counts = {k: int(v) for k, v in pd.Series(y).value_counts().items()}
    return EvaluationReport(
        target=target,
        binary=binary,
        class_counts=counts,
        cv_summary=pd.DataFrame(rows),
        permutation_score=float(obs_score),
        permutation_null_mean=float(perm_scores.mean()),
        permutation_p_value=float(p_val),
        permutation_scores=perm_scores,
    )


def subgroup_fairness_report(
    df: pd.DataFrame,
    target: str = "Social_Weakness",
    positive_label: str = "Yes",
    group_col: str = "Gender",
    n_splits: int = 5,
    random_state: int = 42,
) -> pd.DataFrame:
    """Kişisel alt gruplar (cinsiyet/yaş) için kat dışı tahmin performans ve kalibrasyonu (Brier)."""
    X = df.drop(columns=[target])
    y = (df[target] == positive_label).astype(int)
    pipe = build_candidate_models(list(X.columns), random_state=random_state)[
        "LogisticRegression (L2)"
    ]
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    probs = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    preds = (probs >= 0.5).astype(int)

    rows = []
    for grp, idx in df.groupby(group_col).groups.items():
        y_g = y.loc[idx].to_numpy()
        p_g = probs[df.index.get_indexer(idx)]
        yhat_g = preds[df.index.get_indexer(idx)]
        auc = float(roc_auc_score(y_g, p_g)) if len(np.unique(y_g)) == 2 else float("nan")
        rows.append(
            {
                "group_col": group_col,
                "subgroup": str(grp),
                "n": int(len(y_g)),
                "positive_rate": round(float(y_g.mean()), 4),
                "accuracy": round(float(accuracy_score(y_g, yhat_g)), 4),
                "balanced_accuracy": round(float(balanced_accuracy_score(y_g, yhat_g)), 4),
                "f1_macro": round(float(f1_score(y_g, yhat_g, average="macro")), 4),
                "roc_auc": round(auc, 4),
                "brier_score": round(float(brier_score_loss(y_g, p_g)), 4),
            }
        )
    return pd.DataFrame(rows)


def reproduce_original_bug(df_tr: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    """Orijinal analiz.ipynb hücre 21–23'teki üzerine yazma hatasını (H1) yeniden üretir."""

    def encode_all(frame: pd.DataFrame) -> pd.DataFrame:
        out = frame.copy()
        for col in out.columns:
            if not pd.api.types.is_numeric_dtype(out[col]):
                out[col] = LabelEncoder().fit_transform(out[col])
        return out

    def prepare(frame: pd.DataFrame):
        X = frame.drop(columns=["Sosyal_zayiflik"])
        y = frame["Sosyal_zayiflik"]
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.3, random_state=random_state
        )
        scaler = StandardScaler().fit(X_tr)
        X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)
        X_res, y_res = SMOTE(random_state=random_state).fit_resample(X_tr_s, y_tr)
        return X_res, y_res, X_te_s, y_te

    male = prepare(encode_all(df_tr[df_tr["Cinsiyet"] == "Erkek"]))
    female = prepare(encode_all(df_tr[df_tr["Cinsiyet"] == "Dişi"]))

    factories = {
        "LogisticRegression": lambda: LogisticRegression(),
        "RandomForest": lambda: RandomForestClassifier(random_state=0),
        "SVC": lambda: SVC(),
        "kNN": lambda: KNeighborsClassifier(),
        "GradientBoosting": lambda: GradientBoostingClassifier(random_state=0),
    }

    rows = []
    for name, make in factories.items():
        buggy_male = make().fit(female[0], female[1])
        fixed_male = make().fit(male[0], male[1])
        fixed_female = make().fit(female[0], female[1])
        rows.append(
            {
                "model": name,
                "male_acc_buggy_trained_on_female": round(
                    float(accuracy_score(male[3], buggy_male.predict(male[2]))), 4
                ),
                "male_acc_fixed": round(
                    float(accuracy_score(male[3], fixed_male.predict(male[2]))), 4
                ),
                "female_acc": round(
                    float(accuracy_score(female[3], fixed_female.predict(female[2]))), 4
                ),
            }
        )
    return pd.DataFrame(rows)
