"""Klinik öz-bildirim tarama ölçekleri (PHQ-9, GAD-7) ve Türkçe dilsel belirteç çıkarıcı.

UYARI:
    Bu modüldeki ölçek puanlaması ve dilsel özellikler **klinik tanı aracı değildir**.
    Yalnızca araştırma, eğitim ve profesyonel desteğe yönlendirme desteği içindir.
    PHQ-9 Madde 9 (kendine zarar verme / intihar düşüncesi) ≥ 1 olduğunda acil kriz
    güvenlik bayrağı otomatik olarak tetiklenir.

Kaynaklar:
    - Kroenke, Spitzer & Williams (2001), JGIM — PHQ-9 (duyarlılık %88, özgüllük %88, kesme ≥10)
    - Sarı vd. (2016), Biomedical Research — PHQ-9 Türkçe güvenirlik çalışması
    - Spitzer, Kroenke, Williams & Löwe (2006), Arch Intern Med — GAD-7
    - Konkan vd. (2013), Nöropsikiyatri Arşivi — GAD-7 Türkçe geçerlik/güvenirlik
    - Rude, Gortner & Pennebaker (2004), Cognition and Emotion — 1. tekil şahıs zamirleri
    - Al-Mosaiwi & Johnstone (2018), Clinical Psychological Science — mutlakiyetçi sözcükler
    - Eichstaedt vd. (2018), PNAS — sosyal medya dili ve tıbbi kayıtlarda depresyon
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Sequence

CRISIS_RESOURCES_TR: dict[str, str] = {
    "acil_yardim": "112 Acil Çağrı Merkezi (7/24)",
    "sosyal_destek": "ALO 183 Sosyal Destek Hattı (7/24)",
    "saglik_yonlendirme": "En yakın hastane acil servisi veya Psikiyatri / Ruh Sağlığı Polikliniği",
    "uyari": (
        "Bu tarama aracı tıbbi tanı koymaz. Kendinize zarar verme düşünceniz varsa "
        "lütfen vakit kaybetmeden 112'yi arayın veya güvendiğiniz bir yakınınızla "
        "bir sağlık kuruluşuna başvurun."
    ),
}

PHQ9_ITEMS_TR: tuple[str, ...] = (
    "Bir şeyler yaparken çok az ilgi duyma veya zevk alma",
    "Kendini üzgün, bunalmış veya umutsuz hissetme",
    "Uykuya dalmada/uykuyu sürdürmede zorluk veya çok fazla uyuma",
    "Yorgun hissetme veya enerjinin az olması",
    "İştahsızlık veya aşırı yeme",
    "Kendini kötü hissetme, başarısız olduğunu ya da kendini/aileni hayal kırıklığına uğrattığını düşünme",
    "Gazete okuma veya televizyon izleme gibi işlere odaklanmada zorluk",
    "Başkalarının fark edeceği kadar yavaş hareket etme/konuşma ya da tam tersi aşırı huzursuz/yerinde duramama",
    "Ölmüş olsaydın daha iyi olacağı veya kendine bir şekilde zarar verme düşünceleri",
)

GAD7_ITEMS_TR: tuple[str, ...] = (
    "Sinirli, kaygılı veya çok gergin hissetme",
    "Endişelenmeyi durduramama veya kontrol edememe",
    "Farklı şeyler hakkında çok fazla endişelenme",
    "Gevşemede zorluk çekme",
    "Yerinde duramayacak kadar huzursuz olma",
    "Kolayca kızma veya sinirlenme",
    "Kötü bir şey olacakmış gibi korkma",
)


@dataclass(frozen=True)
class PHQ9Result:
    """PHQ-9 puanlama sonucu ve güvenlik bayrakları."""

    total_score: int
    severity_tr: str
    severity_en: str
    positive_screen: bool
    item9_score: int
    crisis_flag: bool
    recommended_action: str
    crisis_resources: dict[str, str] | None


@dataclass(frozen=True)
class GAD7Result:
    """GAD-7 puanlama sonucu."""

    total_score: int
    severity_tr: str
    severity_en: str
    positive_screen: bool
    recommended_action: str


def _validate_likert(responses: Sequence[int], expected_len: int, scale_name: str) -> list[int]:
    vals = list(responses)
    if len(vals) != expected_len:
        raise ValueError(f"{scale_name} tam olarak {expected_len} madde gerektirir; alınan: {len(vals)}.")
    for idx, v in enumerate(vals, start=1):
        if isinstance(v, bool) or not isinstance(v, int) or not (0 <= v <= 3):
            raise ValueError(
                f"{scale_name} madde {idx} için değer 0 ile 3 arasında tamsayı olmalıdır; alınan: {v!r}."
            )
    return vals


def score_phq9(responses: Sequence[int]) -> PHQ9Result:
    """PHQ-9 (9 madde, her biri 0–3) toplam puanını, şiddet bandını ve kriz bayrağını hesaplar."""
    vals = _validate_likert(responses, expected_len=9, scale_name="PHQ-9")
    total = sum(vals)
    item9 = vals[8]
    crisis = item9 >= 1

    if total <= 4:
        sev_tr, sev_en = "Minimal / Belirti yok", "Minimal"
        action = "Düzenli öz-bakım ve izlem; klinik düzeyde belirti saptanmadı."
    elif total <= 9:
        sev_tr, sev_en = "Hafif depresif belirti", "Mild"
        action = "Belirtilerin 2 hafta sonra yeniden değerlendirilmesi ve destekleyici öz-bakım önerilir."
    elif total <= 14:
        sev_tr, sev_en = "Orta düzey depresif belirti", "Moderate"
        action = "Klinik tarama eşiği (≥10) aşıldı; bir ruh sağlığı uzmanına başvurulması önerilir."
    elif total <= 19:
        sev_tr, sev_en = "Orta-ağır depresif belirti", "Moderately Severe"
        action = "En kısa sürede bir psikiyatri uzmanı veya klinik psikolog ile görüşülmesi önerilir."
    else:
        sev_tr, sev_en = "Ağır depresif belirti", "Severe"
        action = "Öncelikli profesyonel ruh sağlığı değerlendirmesi gerekir."

    if crisis:
        action = (
            "KRİZ GÜVENLİK BAYRAĞI (Madde 9 ≥ 1): Kendine zarar verme düşüncesi bildirildi. "
            "Derhâl acil yardım (112) veya bir ruh sağlığı uzmanıyla iletişime geçilmelidir."
        )

    return PHQ9Result(
        total_score=total,
        severity_tr=sev_tr,
        severity_en=sev_en,
        positive_screen=total >= 10,
        item9_score=item9,
        crisis_flag=crisis,
        recommended_action=action,
        crisis_resources=CRISIS_RESOURCES_TR if crisis else None,
    )


def score_gad7(responses: Sequence[int]) -> GAD7Result:
    """GAD-7 (7 madde, her biri 0–3) toplam puanını ve şiddet bandını hesaplar."""
    vals = _validate_likert(responses, expected_len=7, scale_name="GAD-7")
    total = sum(vals)

    if total <= 4:
        sev_tr, sev_en = "Minimal anksiyete", "Minimal"
        action = "Klinik düzeyde anksiyete belirtisi saptanmadı."
    elif total <= 9:
        sev_tr, sev_en = "Hafif anksiyete", "Mild"
        action = "İzlem ve stres yönetimi alışkanlıklarının desteklenmesi önerilir."
    elif total <= 14:
        sev_tr, sev_en = "Orta düzey anksiyete", "Moderate"
        action = "Klinik tarama eşiği (≥10) aşıldı; uzman değerlendirmesi önerilir."
    else:
        sev_tr, sev_en = "Ağır anksiyete", "Severe"
        action = "Öncelikli profesyonel ruh sağlığı değerlendirmesi önerilir."

    return GAD7Result(
        total_score=total,
        severity_tr=sev_tr,
        severity_en=sev_en,
        positive_screen=total >= 10,
        recommended_action=action,
    )


# ---------------------------------------------------------------------------
# Literatüre dayalı Türkçe dilsel belirteç çıkarıcı (araştırma amaçlı)
# ---------------------------------------------------------------------------

_FIRST_PERSON_SINGULAR_TR: frozenset[str] = frozenset(
    {
        "ben",
        "beni",
        "bana",
        "bende",
        "benden",
        "benim",
        "benimle",
        "bence",
        "kendim",
        "kendimi",
        "kendime",
        "kendimde",
        "kendimden",
        "kendimin",
        "kendimle",
    }
)

# Al-Mosaiwi & Johnstone (2018) 19 sözcüklük mutlakiyetçi sözlüğünün Türkçe karşılıkları
_ABSOLUTIST_SINGLE_TR: frozenset[str] = frozenset(
    {
        "asla",
        "hep",
        "hiç",
        "hiçbir",
        "hiçbiri",
        "hiçkimse",
        "tamamen",
        "tümüyle",
        "bütünüyle",
        "kesinlikle",
        "mutlaka",
        "sürekli",
        "daima",
        "herkes",
        "herkesi",
        "herkese",
        "bütün",
        "tüm",
        "sonsuza",
        "imkansız",
        "imkânsız",
    }
)

_ABSOLUTIST_BIGRAMS_TR: frozenset[tuple[str, str]] = frozenset(
    {
        ("her", "zaman"),
        ("her", "şey"),
        ("her", "şeyi"),
        ("her", "şeyim"),
        ("hiç", "kimse"),
        ("hiç", "bir"),
        ("bir", "daha"),
    }
)

# Al-Mosaiwi & Johnstone (2018)'de belirtilen yanlış-pozitif yumuşatıcı/olumsuzlayıcı bağlamlar
_ABSOLUTIST_QUALIFIERS_TR: frozenset[str] = frozenset(
    {"neredeyse", "hemen", "pek", "değil", "selam", "merhaba", "günaydın"}
)

# Rude vd. (2004) ve Eichstaedt vd. (2018) duygu/somatik/yalnızlık belirteç çekirdekleri
_NEGATIVE_EMOTION_STEMS_TR: tuple[str, ...] = (
    "üzgün",
    "üzülü",
    "umutsuz",
    "çaresiz",
    "değersiz",
    "yalnız",
    "boşluk",
    "ağla",
    "gözyaş",
    "nefret",
    "bıktı",
    "tüken",
    "yorgun",
    "bitkin",
    "mutsuz",
    "keder",
    "acı",
    "bunalt",
    "bunalım",
    "kaygı",
    "endişe",
    "kork",
    "suçlu",
    "pişman",
    "anlamsız",
)

_POSITIVE_EMOTION_STEMS_TR: tuple[str, ...] = (
    "mutlu",
    "sevin",
    "umutlu",
    "huzur",
    "şükür",
    "teşekkür",
    "harika",
    "güzel",
    "keyif",
    "başar",
    "gurur",
    "sevgi",
    "enerjik",
    "rahat",
    "iyiyim",
)

_SOMATIC_SLEEP_STEMS_TR: tuple[str, ...] = (
    "uyku",
    "uyuya",
    "uyana",
    "sabahla",
    "iştah",
    "ağrı",
    "başım",
    "midem",
    "hastane",
    "yorgun",
    "halsiz",
    "nefes",
)

_WORD_RE = re.compile(r"[a-zA-ZçğıöşüÇĞİÖŞÜâîûÂÎÛ]+")


def _turkish_lower(text: str) -> str:
    """Türkçe İ/I harflerini koruyarak küçük harfe çevirir."""
    return text.replace("I", "ı").replace("İ", "i").lower()


@dataclass(frozen=True)
class LinguisticFeatures:
    """Bir Türkçe metinden çıkarılan açıklanabilir psikolinguistik özellikler."""

    word_count: int
    sentence_count: int
    avg_word_length: float
    first_person_singular_ratio: float
    absolutist_ratio: float
    negative_emotion_ratio: float
    positive_emotion_ratio: float
    somatic_sleep_ratio: float
    affect_balance: float
    question_mark_count: int
    exclamation_mark_count: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def extract_turkish_linguistic_features(text: str) -> LinguisticFeatures:
    """Türkçe metinden literatüre dayalı psikolinguistik oranları çıkarır.

    Özellikler (tümü kelime sayısına göre normalize edilir):
        - `first_person_singular_ratio`: Rude vd. (2004), Edwards & Holtzman (2017)
        - `absolutist_ratio`: Al-Mosaiwi & Johnstone (2018) (yumuşatıcı filtresiyle)
        - `negative_emotion_ratio`, `positive_emotion_ratio`, `somatic_sleep_ratio`:
          De Choudhury vd. (2013), Eichstaedt vd. (2018)
    """
    if not text or not text.strip():
        return LinguisticFeatures(
            word_count=0,
            sentence_count=0,
            avg_word_length=0.0,
            first_person_singular_ratio=0.0,
            absolutist_ratio=0.0,
            negative_emotion_ratio=0.0,
            positive_emotion_ratio=0.0,
            somatic_sleep_ratio=0.0,
            affect_balance=0.0,
            question_mark_count=0,
            exclamation_mark_count=0,
        )

    lowered = _turkish_lower(text)
    tokens = _WORD_RE.findall(lowered)
    n = len(tokens)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if n == 0:
        return LinguisticFeatures(
            word_count=0,
            sentence_count=len(sentences),
            avg_word_length=0.0,
            first_person_singular_ratio=0.0,
            absolutist_ratio=0.0,
            negative_emotion_ratio=0.0,
            positive_emotion_ratio=0.0,
            somatic_sleep_ratio=0.0,
            affect_balance=0.0,
            question_mark_count=text.count("?"),
            exclamation_mark_count=text.count("!"),
        )

    fps_count = sum(1 for t in tokens if t in _FIRST_PERSON_SINGULAR_TR)

    abs_count = 0
    for i, tok in enumerate(tokens):
        prev_tok = tokens[i - 1] if i > 0 else ""
        next_tok = tokens[i + 1] if i + 1 < n else ""
        if prev_tok in _ABSOLUTIST_QUALIFIERS_TR or next_tok == "değil":
            continue
        if tok in _ABSOLUTIST_SINGLE_TR:
            abs_count += 1
        elif i + 1 < n and (tok, next_tok) in _ABSOLUTIST_BIGRAMS_TR:
            abs_count += 1

    neg_count = sum(1 for t in tokens if any(t.startswith(s) for s in _NEGATIVE_EMOTION_STEMS_TR))
    pos_count = sum(1 for t in tokens if any(t.startswith(s) for s in _POSITIVE_EMOTION_STEMS_TR))
    som_count = sum(1 for t in tokens if any(t.startswith(s) for s in _SOMATIC_SLEEP_STEMS_TR))

    neg_ratio = neg_count / n
    pos_ratio = pos_count / n

    return LinguisticFeatures(
        word_count=n,
        sentence_count=max(1, len(sentences)),
        avg_word_length=round(sum(len(t) for t in tokens) / n, 3),
        first_person_singular_ratio=round(fps_count / n, 4),
        absolutist_ratio=round(abs_count / n, 4),
        negative_emotion_ratio=round(neg_ratio, 4),
        positive_emotion_ratio=round(pos_ratio, 4),
        somatic_sleep_ratio=round(som_count / n, 4),
        affect_balance=round(pos_ratio - neg_ratio, 4),
        question_mark_count=text.count("?"),
        exclamation_mark_count=text.count("!"),
    )
