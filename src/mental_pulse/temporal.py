"""Erken risk tespiti (CLEF eRisk ERDE / F_latency) ve dijital fenotipleme zaman serisi özellikleri.

Kaynaklar:
    - Losada, D. E., & Crestani, F. (2016). A test collection for research on depression
      and language use. CLEF 2016, LNCS 9822, 28–39. (ERDE metriği)
    - Sadeque, F., Xu, D., & Bethard, S. (2018). Measuring the latency of depression
      detection in social media. WSDM 2018, 495–503. (F_latency metriği)
    - Saeb, S., et al. (2015). Mobile phone sensor correlates of depressive symptom
      severity in daily-life behavior. JMIR, 17(7), e175.
    - Onnela, J.-P., & Rauch, S. L. (2016). Harnessing smartphone-based digital
      phenotyping to enhance behavioral and mental health. Neuropsychopharmacology.
    - De Choudhury, M., et al. (2013). Predicting depression via social media. ICWSM.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from .screening import extract_turkish_linguistic_features


def erde_latency_cost(delay: int, o: int = 5) -> float:
    """Losada & Crestani (2016) geç tespit ceza faktörü lc_o(k) = 1 - 1 / (1 + exp(k - o))."""
    if delay < 1:
        raise ValueError(f"Gecikme (k) en az 1 olmalıdır; alınan: {delay}")
    if o < 1:
        raise ValueError(f"Eşik parametresi (o) en az 1 olmalıdır; alınan: {o}")
    exponent = max(-500.0, min(500.0, float(delay - o)))
    return 1.0 - (1.0 / (1.0 + math.exp(exponent)))


def compute_erde(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    delays: Sequence[int],
    o: int = 5,
    c_fp: float | None = None,
    c_fn: float = 1.0,
    c_tp: float = 1.0,
) -> float:
    """CLEF eRisk Early Risk Detection Error (ERDE_o) metriğini hesaplar (düşük = daha iyi).

    Args:
        y_true: Gerçek ikili etiketler (0 veya 1).
        y_pred: Sistemin ikili kararları (0 veya 1).
        delays: Her kullanıcı için karar verilmeden önce görülen gönderi sayısı (k ≥ 1).
        o: Gecikme ceza eşiği (CLEF eRisk standartları: o=5 ve o=50).
        c_fp: Yanlış pozitif maliyeti; None ise veri setindeki pozitif oranı kullanılır
            (Losada & Crestani, 2016 önerisi).
        c_fn: Yanlış negatif maliyeti (varsayılan 1.0).
        c_tp: Geç doğru pozitif taban maliyeti (varsayılan 1.0 = c_fn).
    """
    yt = list(y_true)
    yp = list(y_pred)
    ks = list(delays)
    if not (len(yt) == len(yp) == len(ks)) or len(yt) == 0:
        raise ValueError("y_true, y_pred ve delays eşit ve sıfırdan büyük uzunlukta olmalıdır.")

    fp_cost = (sum(1 for y in yt if y == 1) / len(yt)) if c_fp is None else float(c_fp)

    errors: list[float] = []
    for truth, pred, k in zip(yt, yp, ks):
        if truth == 0 and pred == 1:
            errors.append(fp_cost)
        elif truth == 1 and pred == 0:
            errors.append(float(c_fn))
        elif truth == 1 and pred == 1:
            errors.append(erde_latency_cost(int(k), o=o) * float(c_tp))
        else:
            errors.append(0.0)
    return float(np.mean(errors))


def compute_f_latency(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    delays: Sequence[int],
    median_ref_delay: float = 10.0,
) -> dict[str, float]:
    """Sadeque, Xu & Bethard (2018) gecikme ağırlıklı F_latency metriğini hesaplar.

    Doğru pozitiflerin gecikmesi arttıkça F1 skoru (1 - median_penalty) ile çarpılarak azaltılır.
    """
    yt = np.asarray(y_true, dtype=int)
    yp = np.asarray(y_pred, dtype=int)
    ks = np.asarray(delays, dtype=float)
    if not (len(yt) == len(yp) == len(ks)) or len(yt) == 0:
        raise ValueError("Girdiler eşit ve boş olmayan diziler olmalıdır.")

    tp_mask = (yt == 1) & (yp == 1)
    tp = int(tp_mask.sum())
    fp = int(((yt == 0) & (yp == 1)).sum())
    fn = int(((yt == 1) & (yp == 0)).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    if tp == 0:
        return {
            "f1": 0.0,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "median_tp_delay": float("nan"),
            "speed": 0.0,
            "f_latency": 0.0,
        }

    p_param = math.log(3.0) / max(1.0, float(median_ref_delay) - 1.0)
    tp_delays = ks[tp_mask]
    penalties = -1.0 + 2.0 / (1.0 + np.exp(-p_param * np.maximum(0.0, tp_delays - 1.0)))
    speed = float(1.0 - np.median(penalties))
    f_lat = float(f1 * speed)
    return {
        "f1": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "median_tp_delay": round(float(np.median(tp_delays)), 2),
        "speed": round(speed, 4),
        "f_latency": round(f_lat, 4),
    }


@dataclass(frozen=True)
class DigitalPhenotypeSummary:
    """Pasif davranış ve zaman serisi dilsel eğilim özet özellikleri (Faz 3 çekirdeği)."""

    home_stay_ratio: float
    location_entropy: float
    normalized_location_entropy: float
    circadian_regularity: float
    night_activity_ratio: float
    mean_absolutist_ratio: float
    absolutist_trend_slope: float
    mean_affect_balance: float
    affect_trend_slope: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def _linear_slope(values: Sequence[float]) -> float:
    arr = np.asarray(values, dtype=float)
    if len(arr) < 2:
        return 0.0
    x = np.arange(len(arr), dtype=float)
    x_centered = x - x.mean()
    denom = float(np.dot(x_centered, x_centered))
    if denom == 0.0:
        return 0.0
    return float(np.dot(x_centered, arr - arr.mean()) / denom)


def extract_digital_phenotype_features(
    location_clusters: Sequence[str],
    hourly_activity_matrix: np.ndarray,
    event_hours: Sequence[int],
    chronological_texts: Sequence[str],
    home_cluster_label: str = "home",
) -> DigitalPhenotypeSummary:
    """Pasif sensör + kronolojik metin akışından dijital fenotipleme özetleri çıkarır.

    Args:
        location_clusters: Zaman pencerelerine göre küme etiketleri (örn. ["home", "work", ...]).
        hourly_activity_matrix: (n_days, 24) boyutlu saatlik aktivite/hareket matrisi.
        event_hours: Dijital etkileşimlerin gerçekleştiği saatler (0–23).
        chronological_texts: Katılımcının zaman sırasına göre dizilmiş Türkçe metinleri.
        home_cluster_label: Ev konumunu temsil eden küme etiketi.
    """
    loc = list(location_clusters)
    if loc:
        home_stay = sum(1 for c in loc if c == home_cluster_label) / len(loc)
        _, counts = np.unique(loc, return_counts=True)
        probs = counts / counts.sum()
        entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
        norm_entropy = float(entropy / math.log(len(counts))) if len(counts) > 1 else 0.0
    else:
        home_stay, entropy, norm_entropy = 0.0, 0.0, 0.0

    mat = np.asarray(hourly_activity_matrix, dtype=float)
    if mat.ndim == 2 and mat.shape[0] >= 2 and mat.shape[1] == 24:
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        valid = (norms[:, 0] > 0)
        if valid.sum() >= 2:
            unit = mat[valid] / norms[valid]
            sim = unit @ unit.T
            triu = sim[np.triu_indices(sim.shape[0], k=1)]
            circadian_reg = float(np.clip(np.mean(triu), 0.0, 1.0))
        else:
            circadian_reg = 0.0
    else:
        circadian_reg = 0.0

    hrs = [int(h) % 24 for h in event_hours]
    night_ratio = (sum(1 for h in hrs if 0 <= h < 5) / len(hrs)) if hrs else 0.0

    if chronological_texts:
        feats = [extract_turkish_linguistic_features(t) for t in chronological_texts]
        abs_series = [f.absolutist_ratio for f in feats]
        aff_series = [f.affect_balance for f in feats]
        mean_abs = float(np.mean(abs_series))
        slope_abs = _linear_slope(abs_series)
        mean_aff = float(np.mean(aff_series))
        slope_aff = _linear_slope(aff_series)
    else:
        mean_abs = slope_abs = mean_aff = slope_aff = 0.0

    return DigitalPhenotypeSummary(
        home_stay_ratio=round(home_stay, 4),
        location_entropy=round(entropy, 4),
        normalized_location_entropy=round(norm_entropy, 4),
        circadian_regularity=round(circadian_reg, 4),
        night_activity_ratio=round(night_ratio, 4),
        mean_absolutist_ratio=round(mean_abs, 4),
        absolutist_trend_slope=round(slope_abs, 4),
        mean_affect_balance=round(mean_aff, 4),
        affect_trend_slope=round(slope_aff, 4),
    )
