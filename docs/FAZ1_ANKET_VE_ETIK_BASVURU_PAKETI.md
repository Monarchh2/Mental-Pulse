# Faz 1 Sahaya Hazır Paket: Etik Kurul Başvurusu, TÜİK Mikro Veri Talebi ve Türkçe Anket Şeması

Bu belge, Mental Pulse projesinin **Faz 0 (RHMCD-20 denetimi)** aşamasından **Faz 1 (geçerlenmiş Türkçe veri ile klinik tahmin modeli geliştirme)** ve **Faz 2 (Türkçe NLP)** aşamalarına geçebilmesi için doğrudan kullanılabilecek üç hazır şablon içerir:

1. **Bölüm A:** Üniversite Etik Kurulu Başvuru Protokolü Taslağı (Riley vd., 2020 örneklem büyüklüğü hesabıyla)
2. **Bölüm B:** TÜİK Türkiye Sağlık Araştırması (EHIS) Mikro Veri Talep Dosyası Taslağı
3. **Bölüm C:** Uygulamaya Hazır Türkçe Anket Formu ve Veri Şeması (KVKK Açık Rıza + PHQ-9 + GAD-7 + OSSS-3 + Demografi + Gönüllü Metin İstemleri)

---

## Bölüm A — Üniversite Etik Kurulu Başvuru Protokolü Taslağı

### A.1 Çalışma Künyesi
- **Araştırmanın Adı:** *Mental Pulse: Türkçe Öz-Bildirim Ölçekleri ve Gönüllü Metin Verilerinden Depresif Belirti Riskinin Sızıntısız ve Açıklanabilir Makine Öğrenmesi ile Taranması*
- **Tasarım:** Gözlemsel, kesitsel (Faz 1) ve isteğe bağlı 2 haftalık kısa boylamsal izlem (Faz 2).
- **Klinik Çerçeve:** Tanı koyma veya tedavi müdahalesi **içermez**; geçerlenmiş öz-bildirim tarama ölçekleri (PHQ-9, GAD-7) üzerinden istatistiksel risk tahmini ve açıklanabilirlik araştırmasıdır.
- **Standartlar:** TRIPOD+AI (Collins vd., 2024, *BMJ*), 6698 sayılı KVKK Madde 6, Kişisel Verileri Koruma Kurulu 2018/10 sayılı karar ve WHO (2021) Sağlıkta Yapay Zekâ Etiği İlkeleri.

### A.2 Dahil Etme ve Dışlama Ölçütleri
- **Dahil etme:** 18 yaş ve üzeri, Türkçe okuyup yazabilen, aydınlatma metnini okuyup özgür iradesiyle elektronik açık rıza veren gönüllü bireyler.
- **Dışlama:** 18 yaş altı bireyler (veli/vasi onamı gerektirdiğinden Faz 1 kapsamı dışındadır), aktif akut psikoz/kriz durumunda bulunanlar (kriz yönlendirmesi sağlanır).

### A.3 Örneklem Büyüklüğü Gerekçesi (Riley vd., 2020, *BMJ* 368:m441)

TRIPOD+AI Madde 8 uyarınca minimum örneklem büyüklüğü [`mental_pulse.fusion.sample_size_riley_binary`](../src/mental_pulse/fusion.py) (`mental-pulse sample-size`) ile **B1 (prevalans ±0,05 hassasiyet)**, **B3 (küçülme faktörü $S \ge 0,90$)** ve **B4 (Nagelkerke $R^2$ iyimserliği $\le 0,05$)** ölçütlerine göre hesaplanmıştır:

| Senaryo | Beklenen PHQ-9 ≥ 10 Oranı | Aday Parametre ($P$) | Beklenen $R^2_{\text{CS}}$ | Önerilen Min. $N$ | Beklenen Pozitif Olay | EPP (Olay / Param.) |
|---|---:|---:|---:|---:|---:|---:|
| **1. Genel Yetişkin Nüfus (TÜİK referansı)** | %6,4 | 15 | 0,0568 (konservatif) | **2.302** | 147,3 | 9,82 |
| **2. Üniversite Öğrencisi Kohortu** | %20,0 | 15 | 0,0949 (konservatif) | **1.347** | 269,4 | 17,96 |
| **3. Klinik Ön Tarama Kohortu** | %30,0 | 15 | 0,1058 (konservatif) | **1.200** | 360,0 | 24,00 |
| **4. Faz 2 Metin + Demografi (yüksek sinyal)** | %20,0 | 20 | 0,1500 | **1.097** | 219,4 | 10,97 |

> **Öneri:** %15 olası eksik/kalite dışı yanıt payı eklenerek üniversite kohortu için hedef **N ≈ 1.550**, genel nüfus için **TÜİK mikro verisi (N ≈ 17.000+)** ile dış geçerleme yapılması planlanmalıdır.

### A.4 Riskler ve Kriz Güvenlik SOP'si (Standart İşletim Prosedürü)
- **Psikolojik rahatsızlık riski:** PHQ-9 sorularının yanıtlanması sırasında katılımcı duygusal hassasiyet yaşayabilir; istediği an anketi sonlandırabilir.
- **Otomatik Kriz Protokolü:** Anket arayüzünde **PHQ-9 Madde 9 ≥ 1** seçildiği anda, toplam puandan bağımsız olarak ekranın üstünde kırmızı güvenlik kartı gösterilir:
  - **112 Acil Çağrı Merkezi (7/24)**
  - **ALO 183 Sosyal Destek Hattı (7/24)**
  - **Üniversite Psikolojik Danışma ve Rehberlik (PDR) Merkezi / En Yakın Psikiyatri Polikliniği**
  - Kod karşılığı: [`mental_pulse.screening.score_phq9`](../src/mental_pulse/screening.py).
- **Veri gizliliği:** İsim, e-posta, telefon ve IP adresi toplanmaz (boylamsal eşleme için katılımcının kendi oluşturduğu anonim 6 haneli kod veya ayrık takma ad anahtarı kullanılır).

### A.5 İstatistiksel Analiz ve Ön Kayıt Planı
- Çalışma başlamadan önce **OSF (Open Science Framework)** üzerinde ön kayıt (preregistration) yapılacaktır (TRIPOD+AI Madde 27).
- Tüm ön işleme adımları `sklearn.pipeline.Pipeline` içinde yalnızca eğitim katlarında öğrenilecek; kişi bazlı tekrarlı ölçümlerde `StratifiedGroupKFold` (`mental_pulse.fusion.evaluate_grouped_multimodal`) kullanılacaktır.
- Başarı yalnızca ham doğrulukla değil **ROC-AUC, PR-AUC, dengeli doğruluk, %90 özgüllükte duyarlılık, Brier skoru, kalibrasyon eğrisi, permütasyon testi ve cinsiyet/yaş alt grup adaleti** ile değerlendirilecektir.

---

## Bölüm B — TÜİK Türkiye Sağlık Araştırması Mikro Veri Talep Taslağı

TÜİK, akademik araştırmacılara **Türkiye Sağlık Araştırması (EHIS)** anonimleştirilmiş mikro verisini (2019 ve 2022/güncel dalgalar; N ≈ 17.000+ yetişkin) resmi taahhütname karşılığında sağlamaktadır. Bu veri seti, Yıldız vd. (2024, *Türk Psikiyatri Dergisi*) tarafından kanıtlandığı gibi **PHQ-8** içerdiği için Mental Pulse'ın **Faz 1A** doğrulaması için en güçlü ulusal kaynaktır.

### B.1 Talep Edilecek Değişken Grupları

| Modül | Değişkenler | Bilimsel Gerekçe |
|---|---|---|
| **Hedef (Outcome)** | PHQ-8'in 8 maddesi (0–3 Likert) + yıllık öz-bildirim depresyon sorusu | Kesme noktası **PHQ-8 ≥ 10** (Kroenke vd., 2009; Yıldız vd., 2024). |
| **Sosyodemografi** | Yaş grubu, cinsiyet, medeni durum, eğitim düzeyi, çalışma durumu, gelir/hane büyüklüğü | Salk vd. (2017); Yıldız vd. (2024) — hem öngörücü hem adalet (fairness) ekseni. |
| **Sosyal Destek** | **Oslo-3 Sosyal Destek Ölçeği (OSSS-3)** 3 maddesi (3–14 puan) | Zayıf sosyal destek depresyonun en güçlü değiştirilebilir risk etkenlerinden biridir. |
| **Sağlık Davranışları** | **IPAQ kısa form** (fiziksel aktivite MET puanı), VKİ (boy/kilo), sigara ve alkol kullanımı | Fiziksel inaktivite depresif belirtilerle pozitif ilişkilidir (Yıldız vd., 2024). |
| **Fiziksel Sağlık** | Algılanan genel sağlık + kronik hastalıklar (hipertansiyon, diyabet, koroner kalp, bel/boyun rahatsızlıkları) | Somatik eş-hastalıklar depresyon riskini anlamlı biçimde artırır. |

### B.2 Başvuru Gerekçesi Özet Metni (Kopyalanabilir Taslak)
> *"Bu araştırma kapsamında, Türkiye Sağlık Araştırması mikro veri setinde yer alan 15 yaş ve üzeri bireylerin Hasta Sağlık Anketi (PHQ-8) depresif belirti skorlarının sosyodemografik özellikler, Oslo-3 Sosyal Destek düzeyi, fiziksel aktivite ve kronik hastalıklar kullanılarak **sızıntısız, kalibre edilmiş ve alt grup adaleti (cinsiyet/yaş) denetlenmiş** makine öğrenmesi modelleriyle (lojistik regresyon, gradyan artırma) öngörülebilirliği incelenecektir. Çalışma TRIPOD+AI (BMJ, 2024) raporlama kılavuzuna uygun olarak yürütülecek; mikro veri hiçbir üçüncü tarafla paylaşılmayacak ve yalnızca toplulaştırılmış istatistiksel bulgular yayımlanacaktır."*

---

## Bölüm C — Faz 1–2 Türkçe Anket Formu ve Veri Şeması

### C.1 Zorunlu Başlangıç: KVKK Aydınlatma ve Açık Rıza Kutucukları
- `[ ]` *(Zorunlu)* 18 yaş ve üzerindeyim; araştırma aydınlatma metnini okudum ve anladım.
- `[ ]` *(Zorunlu)* Yanıtlarımın 6698 sayılı KVKK Madde 6 kapsamında anonim/takma adlı olarak yalnızca bilimsel araştırma amacıyla işlenmesine açık rıza veriyorum.
- `[ ]` *(Zorunlu)* Bu formun tıbbi tanı veya tedavi sağlamadığını, acil durumlarda 112'ye veya bir sağlık kuruluşuna başvurmam gerektiğini anlıyorum.
- `[ ]` *(İsteğe bağlı — Faz 2)* Gönüllü açık uçlu metin yanıtlarımın kimliksizleştirilmiş biçimde Türkçe doğal dil işleme araştırmasında kullanılmasına izin veriyorum.

### C.2 Anket Blokları ve Önerilen Sütun Şeması

| Blok | Sütun Adları | Ölçek / Tip | Referans |
|---|---|---|---|
| **1. Demografi** | `age_group`, `gender`, `education`, `marital_status`, `occupation`, `chronic_illness` | Kategorik (standart kodlu) | Yıldız vd. (2024) |
| **2. Sosyal Destek (OSSS-3)** | `osss_1`, `osss_2`, `osss_3`, `osss_total` | 3–14 puan (3–8 zayıf, 9–11 orta, 12–14 güçlü) | Kocalevent vd. (2018); Yıldız vd. (2024) |
| **3. PHQ-9 (Türkçe)** | `phq9_1` … `phq9_9`, `phq9_total`, `phq9_positive` ($\ge 10$), `crisis_flag` (`phq9_9 >= 1`) | 0–3 Likert × 9 (0–27) | Kroenke vd. (2001); Güleç vd. (2012); Sarı vd. (2016) |
| **4. GAD-7 / YAB-7 (Türkçe)** | `gad7_1` … `gad7_7`, `gad7_total`, `gad7_positive` ($\ge 10$) | 0–3 Likert × 7 (0–21) | Spitzer vd. (2006); Konkan vd. (2013) |
| **5. Davranışsal Özet** | `sleep_hours_avg`, `physical_activity_days`, `screen_time_hours`, `outdoor_days_per_week` | Sayısal / sürekli | Saeb vd. (2015) ile karşılaştırılabilir sürekli ölçüm |
| **6. Gönüllü Metin (Faz 2)** | `free_text_week`, `free_text_stress` | Açık uçlu Türkçe metin (min. 50 kelime önerilir; kişisel isim yazılmaması istenir) | Rude vd. (2004); Al-Mosaiwi & Johnstone (2018); Eichstaedt vd. (2018) |

#### Gönüllü Metin İstemleri (Örnek)
1. *"Son iki haftanızın genel olarak nasıl geçtiğini kendi cümlelerinizle (kişi veya kurum adı vermeden) kısaca anlatır mısınız?"*
2. *"Son günlerde sizi en çok zorlayan ya da iyi hissettiren durumlar neler oldu?"*

> **Otomatik özellik çıkarımı:** Bu metinler toplandığında doğrudan [`TurkishPsycholinguisticTransformer`](../src/mental_pulse/fusion.py) ve [`scripts/train_berturk_template.py`](../scripts/train_berturk_template.py) ile kişi bazlı `StratifiedGroupKFold` altında eğitilebilir.
