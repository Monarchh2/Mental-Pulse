"""ERDE/F_latency erken tespit metrikleri, dijital fenotipleme, Riley (2020) örneklem ve çok kipli grup-CV testleri."""

import numpy as np
import pandas as pd
import pytest

from mental_pulse.fusion import (
    TurkishPsycholinguisticTransformer,
    evaluate_grouped_multimodal,
    sample_size_riley_binary,
)
from mental_pulse.temporal import (
    compute_erde,
    compute_f_latency,
    erde_latency_cost,
    extract_digital_phenotype_features,
)


def test_erde_rewards_early_detection_over_late_detection():
    y_true = [1, 1, 0, 0]
    y_pred = [1, 1, 0, 0]
    early_delays = [2, 3, 10, 10]
    late_delays = [20, 30, 10, 10]

    erde_early = compute_erde(y_true, y_pred, early_delays, o=5)
    erde_late = compute_erde(y_true, y_pred, late_delays, o=5)
    assert erde_early < erde_late
    assert 0.0 <= erde_early < 0.1
    assert erde_late > 0.45

    # k == o iken lc_o(k) tam olarak 0.5'tir
    assert abs(erde_latency_cost(5, o=5) - 0.5) < 1e-9


def test_f_latency_penalizes_slow_true_positives():
    y_true = [1, 1, 0, 0]
    y_pred = [1, 1, 0, 0]
    fast = compute_f_latency(y_true, y_pred, [1, 2, 10, 10], median_ref_delay=10.0)
    slow = compute_f_latency(y_true, y_pred, [15, 25, 10, 10], median_ref_delay=10.0)
    assert fast["f1"] == slow["f1"] == 1.0
    assert fast["f_latency"] > slow["f_latency"]


def test_digital_phenotype_contrasts_isolated_vs_regular_profiles():
    # İzole, düzensiz sirkadiyen ritim, gece aktif, kötüleşen dil eğilimi
    rng = np.random.default_rng(7)
    irregular = rng.uniform(0.0, 1.0, size=(7, 24))
    dep_profile = extract_digital_phenotype_features(
        location_clusters=["home"] * 18 + ["shop", "home"],
        hourly_activity_matrix=irregular,
        event_hours=[1, 2, 3, 4, 2, 14, 23, 1],
        chronological_texts=[
            "Bugün biraz yorgunum ama idare ediyorum.",
            "Ben hep yalnız hissediyorum, geceleri uyuyamıyorum.",
            "Ben asla düzelmeyeceğim, hiçbir şey iyi değil, tamamen tükendim ve umutsuzum.",
        ],
    )

    # Düzenli sirkadiyen ritim, yüksek konum çeşitliliği, gündüz aktif, olumlu dil
    base_day = np.array([0, 0, 0, 0, 0, 0, 1, 3, 5, 6, 5, 4, 5, 6, 5, 4, 5, 4, 3, 2, 1, 1, 0, 0], dtype=float)
    regular = np.vstack([base_day + rng.normal(0, 0.1, size=24).clip(0) for _ in range(7)])
    healthy_profile = extract_digital_phenotype_features(
        location_clusters=["home", "work", "gym", "park", "cafe"] * 4,
        hourly_activity_matrix=regular,
        event_hours=[9, 10, 12, 14, 16, 18, 20, 21],
        chronological_texts=[
            "Güzel bir sabah yürüyüşü yaptık, çok enerjik ve huzurluyum.",
            "Arkadaşlarla keyifli kahve içtik, harika bir gün oldu.",
            "Spor sonrası oldukça mutlu ve rahat hissediyorum, teşekkürler.",
        ],
    )

    assert dep_profile.home_stay_ratio > healthy_profile.home_stay_ratio
    assert dep_profile.normalized_location_entropy < healthy_profile.normalized_location_entropy
    assert dep_profile.circadian_regularity < healthy_profile.circadian_regularity
    assert dep_profile.night_activity_ratio > healthy_profile.night_activity_ratio
    assert dep_profile.absolutist_trend_slope > 0
    assert dep_profile.mean_affect_balance < healthy_profile.mean_affect_balance


def test_riley_sample_size_matches_published_benchmarks():
    # Riley vd. (2020, BMJ): p=0.5 için yalnızca prevalans ölçütü B1 -> 385 kişi
    r_half = sample_size_riley_binary(prevalence=0.5, n_parameters=1)
    assert r_half.n_criterion_1_prevalence == 385
    assert abs(r_half.max_r2_cs - 0.75) < 1e-6

    # Düşük prevalans + daha fazla parametre daha büyük örneklem gerektirir
    r_tr = sample_size_riley_binary(prevalence=0.064, n_parameters=15)
    r_high = sample_size_riley_binary(prevalence=0.25, n_parameters=15)
    assert r_tr.recommended_min_n > r_high.recommended_min_n
    assert r_tr.events_per_parameter > 0

    with pytest.raises(ValueError):
        sample_size_riley_binary(prevalence=0.0, n_parameters=10)


def test_grouped_multimodal_pipeline_prevents_participant_leakage_and_learns_signal():
    # Kontrollü sentetik simülasyon (Faz 2 boru hattı doğrulaması içindir)
    dep_templates = [
        "Ben her zaman kendimi yalnız ve umutsuz hissediyorum, geceleri uyuyamıyorum.",
        "Hiçbir şey asla düzelmeyecek, ben tamamen tükendim ve çok üzgünüm.",
        "Sürekli yorgun ve çaresizim, kimse beni anlamıyor, hep boşluktayım.",
    ]
    pos_templates = [
        "Bugün arkadaşlarla harika bir yürüyüş yaptık, çok huzurlu ve mutluyum.",
        "Spor ve kahve sonrası oldukça enerjik ve keyifli hissediyorum.",
        "Güzel bir hafta oldu, başardığımız işten gurur ve sevinç duyuyorum.",
    ]

    rng = np.random.default_rng(42)
    rows = []
    for pid in range(40):
        label = int(pid < 20)
        for j in range(3):
            txt = dep_templates[(pid + j) % 3] if label else pos_templates[(pid + j) % 3]
            rows.append(
                {
                    "participant_id": f"P{pid:03d}",
                    "text": txt,
                    "gender": "Female" if pid % 2 == 0 else "Male",
                    "home_stay_ratio": float(rng.normal(0.85 if label else 0.45, 0.08)),
                    "circadian_regularity": float(rng.normal(0.45 if label else 0.85, 0.08)),
                    "phq9_positive": label,
                }
            )
    sim_df = pd.DataFrame(rows)

    tf = TurkishPsycholinguisticTransformer()
    X_ling = tf.fit_transform(sim_df["text"])
    assert X_ling.shape == (len(sim_df), 11)

    res = evaluate_grouped_multimodal(
        sim_df,
        target_col="phq9_positive",
        group_col="participant_id",
        text_col="text",
        categorical_cols=["gender"],
        numeric_cols=["home_stay_ratio", "circadian_regularity"],
        n_splits=5,
        calibrate=True,
        random_state=42,
    )
    assert res["n_unique_groups"] == 40
    assert res["oof_roc_auc"] > 0.90
    assert res["oof_brier_score"] < 0.15
