"""PHQ-9/GAD-7 tarama puanlaması, kriz güvenlik bayrağı ve Türkçe dilsel özellik testleri."""

import pytest

from mental_pulse.screening import (
    extract_turkish_linguistic_features,
    score_gad7,
    score_phq9,
)


def test_phq9_severity_bands_and_positive_screen():
    r_min = score_phq9([0, 1, 0, 1, 0, 0, 1, 0, 0])
    assert r_min.total_score == 3
    assert r_min.severity_en == "Minimal"
    assert not r_min.positive_screen
    assert not r_min.crisis_flag
    assert r_min.crisis_resources is None

    r_mod = score_phq9([2, 2, 1, 2, 1, 1, 1, 0, 0])
    assert r_mod.total_score == 10
    assert r_mod.severity_en == "Moderate"
    assert r_mod.positive_screen
    assert not r_mod.crisis_flag

    r_sev = score_phq9([3, 3, 3, 3, 3, 3, 2, 2, 0])
    assert r_sev.total_score == 22
    assert r_sev.severity_en == "Severe"
    assert r_sev.positive_screen


def test_phq9_item9_triggers_crisis_protocol_even_when_total_low():
    r = score_phq9([0, 0, 0, 0, 0, 0, 0, 0, 1])
    assert r.total_score == 1
    assert r.item9_score == 1
    assert r.crisis_flag is True
    assert r.crisis_resources is not None
    assert "112" in r.crisis_resources["acil_yardim"]


def test_phq9_and_gad7_validation_errors():
    with pytest.raises(ValueError):
        score_phq9([0, 1, 2])
    with pytest.raises(ValueError):
        score_phq9([0, 1, 2, 0, 0, 0, 0, 0, 4])
    with pytest.raises(ValueError):
        score_phq9([True, 0, 0, 0, 0, 0, 0, 0, 0])
    with pytest.raises(ValueError):
        score_gad7([0, 1, 2, 3, 0, 1])


def test_gad7_scoring():
    r = score_gad7([2, 2, 2, 1, 1, 1, 1])
    assert r.total_score == 10
    assert r.severity_en == "Moderate"
    assert r.positive_screen is True


def test_turkish_linguistic_features_differentiates_depressive_vs_positive_text():
    depressive = (
        "Ben her zaman kendimi çok yalnız ve umutsuz hissediyorum. "
        "Hiçbir şey asla düzelmeyecek, tamamen tükendim ve geceleri uyuyamıyorum."
    )
    positive = (
        "Bugün yürüyüş yaptık, çok güzel ve huzurlu bir gündü. "
        "Arkadaşlarla keyifli sohbet ettik, oldukça enerjik ve mutluyuz."
    )
    f_dep = extract_turkish_linguistic_features(depressive)
    f_pos = extract_turkish_linguistic_features(positive)

    assert f_dep.first_person_singular_ratio > f_pos.first_person_singular_ratio
    assert f_dep.absolutist_ratio > f_pos.absolutist_ratio
    assert f_dep.negative_emotion_ratio > f_pos.negative_emotion_ratio
    assert f_dep.somatic_sleep_ratio > f_pos.somatic_sleep_ratio
    assert f_dep.affect_balance < 0
    assert f_pos.affect_balance > 0


def test_absolutist_false_positive_filter():
    # "merhaba herkes" ve "neredeyse tamamen" yanlış pozitif olarak elenmelidir
    salutation = extract_turkish_linguistic_features("Merhaba herkes, bugün neredeyse tamamen bitti.")
    assert salutation.absolutist_ratio == 0.0


def test_empty_text_returns_zeros():
    f = extract_turkish_linguistic_features("   ")
    assert f.word_count == 0
    assert f.absolutist_ratio == 0.0
