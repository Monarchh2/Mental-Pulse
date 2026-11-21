# Literatür Karşılaştırma Matrisi ve Mental Pulse Tasarım Çıkarımları

Bu belge, Mental Pulse projesi için taranan **epidemiyoloji, klinik psikometri, karantina psikolojisi, makine öğrenmesi, doğal dil işleme (NLP), dijital fenotipleme, yöntemsel güvenlik (sızıntı/raporlama) ve yapay zekâ etiği** literatürünü sistematik bir matris hâlinde özetler. Her çalışmanın bulguları doğrudan Mental Pulse'ın veri, model, değerlendirme ve etik kararlarına bağlanmıştır.

---

## 1. Epidemiyoloji ve Karantina Psikolojisi

| Çalışma | Yayın / Tür | Kapsam / Örneklem | Ölçek / Veri | Temel Bulgu | Kısıtlar | Mental Pulse'a Çıkarımı |
|---|---|---|---|---|---|---|
| **WHO (2026)** | DSÖ Bilgi Notu | Küresel (2023 GBD) | Küresel hastalık yükü tahminleri | Yetişkinlerde %5,2 depresyon (kadın %6,2, erkek %4,1; ≈322 milyon kişi); yüksek gelirli ülkelerde bile yalnızca ≈1/3 tedavi alıyor; 2021'de ≈727.000 intihar (15–29 yaşta 3. ölüm nedeni). | Ülkeler arası kayıt farklılıkları. | Erken tespit ve ölçeklenebilir tarama ihtiyacını doğrular; kriz protokolünün zorunluluğunu ortaya koyar. |
| **COVID-19 Mental Disorders Collaborators (2021)** | *The Lancet*, 398:1700–1712 | 204 ülke ve bölge (2020) | Sistematik derleme + meta-regresyon | 2020'de majör depresyonda **+%27,6** (+53,2 milyon vaka), anksiyetede **+%25,6** (+76,2 milyon vaka). Kadınlarda ve gençlerde artış daha belirgin. | Pandeminin erken dönemindeki veri eksikliği. | Cinsiyet ve yaş, depresyon modellerinde hem güçlü öngörücü hem de alt grup adalet ekseni olmalıdır. |
| **Brooks vd. (2020)** | *The Lancet*, 395:912–920 | 3166 makaleden 24'ü (hızlı derleme) | Önceki salgın karantinaları (SARS, Ebola vb.) | Karantina; TSSB, öfke ve kafa karışıklığını artırıyor. Başlıca stresörler: uzun karantina, enfeksiyon korkusu, hayal kırıklığı, can sıkıntısı, bilgi/malzeme eksikliği, maddi kayıp, damgalanma. | SARS/Ebola döneminden kesitsel çalışmalar ağırlıkta. | RHMCD-20'deki `Days_Indoors` ve `Quarantine_Frustrations` kuramsal olarak anlamlıdır; ancak finansal kayıp, sosyal destek ve korku eksiktir. |
| **Prati & Mancini (2021)** | *Psychological Medicine*, 51:201–211 | 25 boylamsal çalışma + doğal deney | Meta-analiz & meta-regresyon | Kapanmaların ruh sağlığı üzerindeki etkisi **anlamlı fakat küçük**; **kapanma süresi bu etkiyi anlamlı biçimde düzenlemiyor**. | Çalışmalar arası heterojenlik, ağırlıklı yüksek gelirli ülkeler. | Yalnızca "evde kalınan gün sayısı" gibi tekil bir anket maddesinden yüksek tahmin gücü beklemek gerçekçi değildir. |
| **Hosen, al-Mamun & Mamun (2021)** | *Global Mental Health*, 8:e47 | 24 Bangladeş çalışması (n = 49.806) | Çevrim içi kesitsel anketler (çoğunlukla DASS-21, PHQ-9, GAD-7) | Havuzlanmış yaygınlık: depresyon **%47**, anksiyete **%47**, stres **%44**; öğrencilerde depresyon **%65**. Cinsiyet, yaş, gelir, eğitim, egzersiz, kronik hastalık ve sosyal medya maruziyeti tutarlı risk etkenleri. | Çok yüksek heterojenlik ($I^2 > \%99$), kolayda örnekleme, öz-bildirim. | RHMCD-20 ile **aynı ülke ve dönemde** cinsiyet/yaş/meslek güçlü risk etkeniyken RHMCD-20'de hepsinin sıfıra yakın olması veri kalitesi sorununu kanıtlar. |
| **Salk, Hyde & Abramson (2017)** | *Psychological Bulletin*, 143:783–822 | Temsilî ulusal örneklemler (meta-analiz) | Klinik tanılar + belirti ölçekleri | Majör depresyon tanısında kadın/erkek olasılık oranı **OR ≈ 1,95**; fark ergenlikte zirve yapar ve yetişkinlikte sürer. | Kesitsel ağırlık, kültürler arası bildirim farkları. | RHMCD-20'de cinsiyetin depresif belirteçlerle anlamsız çıkması literatürle çelişir; cinsiyet modelden atılmamalıdır. |
| **Yıldız vd. (2024)** | *Türk Psikiyatri Dergisi*, 35(3):167–177 | Türkiye nüfusu, n = 17.084 (≥15 yaş), TÜİK 2019 | **PHQ-8**, IPAQ, Oslo-3 Sosyal Destek (OSSS-3), kronik hastalıklar | Noktasal depresif belirti (PHQ-8 ≥ 10) **%6,4**; hafif belirti %20,8; yıllık öz-bildirim %10,1. Kadınlarda **OR = 1,52**. Eğitim, fiziksel aktivite, evlilik ve sosyal destek koruyucu; kronik hastalık risk artırıcı. Lojistik regresyon Nagelkerke $R^2 = 0,65$. | Kesitsel tasarım; kurumsal nüfus hariç. | **Faz 1 için en güçlü referans:** Türkiye'de PHQ-8 + sosyodemografi + sosyal destek + kronik hastalık birleşimi, basit modellerle bile yüksek açıklayıcılık sağlar. |

---

## 2. Klinik Psikometrik Ölçekler (Etiket / Ground Truth)

| Çalışma | Yayın | Ölçek | Psikometrik Performans | Mental Pulse'a Çıkarımı |
|---|---|---|---|---|
| **Kroenke, Spitzer & Williams (2001)** | *J Gen Intern Med*, 16:606–613 | **PHQ-9** (9 madde, 0–27) | Kesme noktası **≥10**: majör depresyon için **duyarlılık %88, özgüllük %88**. Şiddet bantları: 5/10/15/20. | `src/mental_pulse/screening.py` içinde birebir uygulandı; Faz 1–3 veri toplamasında birincil hedef etiket olarak önerilir. |
| **Güleç vd. (2012) & Sarı vd. (2016)** | *Comprehensive Psychiatry* / *Biomedical Research* | **PHQ-9 Türkçe** | Türk popülasyonunda geçerli ve güvenilir uyarlama. | Türkiye hedefli tarama ve etiketleme için hazır ve geçerlenmiş araç. |
| **Spitzer, Kroenke, Williams & Löwe (2006)** | *Arch Intern Med*, 166:1092–1097 | **GAD-7** (7 madde, 0–21) | Yaygın anksiyete bozukluğu için kesme noktası **≥10** (duyarlılık %89, özgüllük %82). | Depresyonla yüksek eş-tanı (komorbidite) oranı nedeniyle PHQ-9'a eşlikçi tarama ölçeği olarak `screening.py`'ye eklendi. |
| **Konkan vd. (2013)** | *Nöropsikiyatri Arşivi*, 50:53–58 | **GAD-7 Türkçe (YAB-7)** | Türkçe uyarlama, geçerlik ve güvenirlik doğrulandı. | Türkiye örnekleminde ikincil etiket kaynağı. |
| **Amin, Salehin, Baten & Al Noman (2024)** | *Data in Brief*, 54:110376 | **RHMCD-20** (13 madde, n = 824/825) | Geçerlik/güvenirlik testi yok; standart klinik ölçek yok; eksik değerler ortalama ile doldurulmuş; dokümantasyon-CSV uyumsuzlukları var. | Yalnızca "negatif kontrol / yöntem kıyaslama" verisi olarak tutulmalı; klinik tahmin için **kullanılmamalı**. |

---

## 3. Sosyal Medya, Doğal Dil İşleme (NLP) ve Psikolinguistik

| Çalışma | Yayın | Veri / Etiket | Yöntem | Temel Bulgu | Mental Pulse'a Çıkarımı |
|---|---|---|---|---|---|
| **Rude, Gortner & Pennebaker (2004)** | *Cognition and Emotion*, 18:1121–1133 | Üniversite öğrencisi yazıları (depresif, geçmişte depresif, hiç depresif olmayan) | LIWC sözcük sayımı | Depresif bireyler daha fazla **1. tekil şahıs zamiri** ("ben", "benim") ve olumsuz duygu sözcüğü, daha az olumlu sözcük kullanır. | `extract_turkish_linguistic_features()` içinde `first_person_singular_ratio` ve `affect_balance` özelliklerinin kuramsal temeli. |
| **De Choudhury, Gamon, Counts & Horvitz (2013)** | *AAAI ICWSM*, 7:128–137 | Twitter (n = 476 kitle kaynaklı, **CES-D** etiketi) | SVM, duygu/etkileşim/gece aktivitesi/LIWC özellikleri | Depresyon başlangıcı öncesi davranışsal değişimler (düşük etkileşim, artan gece aktivitesi, benlik odaklı dil, olumsuz duygu) ≈%70 doğrulukla ayrıştırılabildi. | README'deki "dijital profil + zaman serisi" vizyonunun kurucu referansı. |
| **Guntuku vd. (2017)** | *Curr Opin Behav Sci*, 18:43–49 | Sosyal medya çalışmaları bütünleştirici derleme | Sözlük, konu modelleme, ML | Etiket kalitesi (öz-bildirim tanı vs. ölçek vs. forum üyeliği) model genellenebilirliğini doğrudan belirler. | Zayıf anahtar kelime etiketlerinden kaçınılmalı; PHQ-9 gibi ölçekler tercih edilmeli. |
| **Al-Mosaiwi & Johnstone (2018)** | *Clinical Psychological Science*, 6(4):529–542 | 63 internet forumu (>6.400 üye), kontrol + anksiyete/depresyon/intihar/iyileşme | 19 sözcüklük **mutlakiyetçi sözlük** + LIWC + çok düzeyli karma model | Mutlakiyetçi sözcükler ("asla, hep, tamamen, hiçbir...") kontrol (%0,97) < depresyon/anksiyete (%1,45, $d > 3,14$) < intihar düşüncesi (%1,80, $d > 1,71$). Olumsuz duygu sözcüklerinden bile daha iyi şiddet izliyor; iyileşmede de yüksek (%1,31 → bilişsel yatkınlık). | `screening.py`'ye **Türkçe mutlakiyetçi sözlük + yanlış-pozitif filtresi** (olumsuzlama/selamlama elemesi) eklendi. |
| **Eichstaedt vd. (2018)** | *PNAS*, 115(44):11203–11208 | 683 rıza veren acil servis hastası (114'ü EMR'de depresyon tanılı; 1:5 kontrol) | Facebook metni (524.292 gönderi), 200 LDA konusu + n-gram + LIWC, Ridge lojistik regresyon | İlk tıbbi tanıdan *önceki* dille **AUC = 0,69**; son 6 ayla **AUC = 0,72**; **3 ay öncesinden** anlamlı tahmin (AUC = 0,62, p = 0,002). Dil özellikleri demografiden (AUC = 0,57) açık ara üstün. | Gerçek klinik tanıyı metinle öngörmenin üst sınırını (~0,70–0,72 AUC) gerçekçi biçimde tanımlar; uçuk %95+ iddialarından kaçınmak için referans. |
| **Chancellor & De Choudhury (2020)** | *npj Digital Medicine*, 3:43 | 75 sosyal medya ruh sağlığı tahmin çalışması (eleştirel derleme) | Yöntem değerlendirmesi | Kronik sorunlar: **yapı geçerliği eksikliği**, bulanık temel gerçek, zayıf klinik bağ, yetersiz raporlama ve etik/rıza boşlukları. | Faz 2 veri protokolünde etik kurul + açık rıza + klinik ölçek şart koşuldu. |
| **Losada, Crestani & Parapar (CLEF eRisk, 2017–2025)** | *CLEF Working Notes / LNCS* | Reddit kullanıcı gönderi akışları (çok yıllık ortak görev) | Sıralı erken risk tespiti, **ERDE** metriği | Yalnızca "doğru tahmin" değil **ne kadar erken** (kaç gönderide) tespit edildiği de cezalandırılır. | Mental Pulse'ın "erken tespit" iddiası Faz 2–3'te ERDE benzeri zamana duyarlı metrikle ölçülmelidir. |
| **Schweter (2020; v2 2025)** | *Zenodo* | Türkçe metin derlemi | **BERTurk** (`dbmdz/bert-base-turkish-cased`) | Türkçe NLP görevlerinde (duygu analizi, metin sınıflandırma) standart dönüştürücü (Transformer) tabanı. | Faz 2'de Türkçe depresif belirti sınıflandırıcısı için önerilen önceden eğitilmiş model. |
| **JMIR (2025) & Frontiers in AI (2025)** | *JMIR* 27:e59002 / *Front AI* 1627078 | Sosyal medya metin tabanlı depresyon tahmini meta-analizi + XAI | Sistematik derleme + SHAP/LIME açıklanabilir modeller | Transformer/hibrit modeller performans artırsa da yanlılık, örneklem dengesizliği ve açıklanabilirlik klinik benimseme için kritik engel olmayı sürdürüyor. | Mimariye zorunlu **SHAP açıklanabilirlik** katmanı eklendi. |

---

## 4. Dijital Fenotipleme ve Pasif Algılama

| Çalışma | Yayın | Veri / Sensör | Temel Bulgu | Mental Pulse'a Çıkarımı |
|---|---|---|---|---|
| **Saeb vd. (2015)** | *JMIR*, 17(7):e175 | Akıllı telefon GPS + kullanım verisi, **PHQ-9** | Sirkadiyen hareket düzenliliği (24 saatlik ritim) ile depresif belirti şiddeti arasında güçlü negatif korelasyon (**$r = -0,63$**); konum çeşitliliği ve evde kalma süresi anlamlı ilişkili. | RHMCD-20'deki öz-bildirim `Days_Indoors` sorusunun **nesnel, sürekli ve zaman serisi** karşılığıdır (Faz 3). |
| **Onnela & Rauch (2016)** | *Neuropsychopharmacology*, 41:1691–1696 | Akıllı telefon tabanlı pasif ve aktif veri | "Dijital fenotipleme": bireyin doğal ortamında anlık, pasif davranışsal ölçümü. | Sistem mimarisinin sensör/davranış katmanının kuramsal çerçevesi. |
| **Torous vd. (2021; 2025 güncelleme)** | *World Psychiatry*, 20(3):318–335 | Dijital psikiyatri (uygulamalar, sosyal medya, sohbet botları, VR) | Kanıt temeli hızla büyüse de klinik entegrasyon, uzun vadeli kullanıcı bağlılığı, gizlilik ve kanıta dayalı standartlaştırma hâlâ en büyük darboğazlar. | Faz 4 prototipinde klinik iş akışı uyumu ve kullanıcı güveni önceliklendirildi. |

---

## 5. Makine Öğrenmesi Metodolojisi, Sızıntı, Raporlama ve Etik

| Çalışma | Yayın | Odak | Temel Bulgu / Standart | Mental Pulse'a Çıkarımı |
|---|---|---|---|---|
| **Shatte, Hutchinson & Teague (2019)** | *Psychological Medicine*, 49:1426–1448 | Ruh sağlığında ML kapsam derlemesi (300 çalışma) | En sık alan depresyon/tanı; çoğu çalışma küçük örneklem ve iç geçerleme ile sınırlı; çok disiplinli (klinisyen + bilgisayar bilimci) ekipler gerekli. | Mental Pulse'da psikiyatri/psikoloji uzman danışmanlığı zorunlu kılındı. |
| **Chekroud vd. (2021)** | *World Psychiatry*, 20(2):154–170 | Psikiyatride tedavi sonucu tahmini | İç çapraz doğrulamada yüksek görünen modeller **dış klinik örneklemlerde** sıkça şansa yakınsar; dış geçerleme ve prospektif test şarttır. | Değerlendirme protokolüne dış geçerleme ve kalibrasyon eklendi. |
| **Blagus & Lusa (2013)** | *BMC Bioinformatics*, 14:106 | SMOTE analizi | SMOTE, sınıf dengesizliği olmayan veya yüksek boyutlu verilerde fayda sağlamaz; test bölmesinden önce uygulanırsa yapay iyimserlik (sızıntı) üretir. | Orijinal defterde dengeli sınıflara SMOTE uygulanması gereksizdi; `analiz_v2` ve `modeling.py`'de kaldırıldı. |
| **Kapoor & Narayanan (2023)** | *Patterns*, 4(9):100804 | ML tabanlı bilimde veri sızıntısı (17 alan, 294 makale) | Ön işlemenin tüm veride yapılması, tekrarlayan örneklerin eğitim/teste bölünmesi ve zaman sızıntısı yaygındır; sızıntı düzeltildiğinde iddialar sıklıkla çöker. | Tüm ön işleme `sklearn.pipeline.Pipeline` içinde eğitim katına izole edildi; kişi bazlı gruplanmış CV kuralı konuldu. |
| **Collins vd. (2024) — TRIPOD+AI** | *BMJ*, 385:e078378 | Klinik tahmin modelleri (regresyon & ML) raporlama kılavuzu | 27 maddelik standart: veri kaynağı, sonuç tanımı, eksik veri, örneklem büyüklüğü, ayrım + kalibrasyon, alt grup adaleti, şeffaflık. | `docs/TRIPOD_AI_KONTROL_LISTESI.md` belgesinde madde madde uygulandı. |
| **Gebru vd. (2021)** | *Communications of the ACM*, 64(12):86–92 | *Datasheets for Datasets* | Her veri seti motivasyon, bileşim, toplama, ön işleme, uygun/uygunsuz kullanım ve bakım başlıklarıyla belgelenmelidir. | `docs/VERI_KARTI_RHMCD20.md` belgesinde RHMCD-20 için uygulandı. |
| **WHO (2021)** | DSÖ Kılavuzu (ISBN 9789240029200) | Sağlıkta YZ Etiği ve Yönetişimi | 6 temel ilke: insan özerkliği, refah/güvenlik, şeffaflık/açıklanabilirlik, hesap verebilirlik, kapsayıcılık/hakkaniyet, sürdürülebilirlik. | `docs/ETIK_VE_KVKK_CERCEVESI.md` belgesinin etik sütununu oluşturur. |
| **KVKK (6698 sayılı Kanun, Md. 6)** | T.C. Mevzuatı & Kurul Kararı 2018/10 | Özel nitelikli kişisel sağlık verileri | Sağlık verileri özel nitelikli veridir; açık rıza / sınırlı istisnalar ve Kurul'un yeterli güvenlik önlemleri olmadan işlenemez. | Veri toplama, takma adlandırma, şifreleme ve imha politikaları buna göre tasarlandı. |

---

## 6. Sentez: Literatürden Doğan 7 Temel Tasarım Kuralı

1. **Etiket her şeydir:** Klinik geçerliği kanıtlanmış ölçek (PHQ-9 / PHQ-8, GAD-7) olmadan "depresyon tespiti" iddia edilemez.
2. **Önce basit ve yorumlanabilir taban:** Demografi + sosyal destek tabanlı lojistik regresyon (ve `DummyClassifier`) her deneyde referans olmalıdır.
3. **Dil sinyali tablo anketinden güçlü, ancak gerçekçi tavan ~0,70–0,75 AUC:** Eichstaedt vd. (2018) ve Al-Mosaiwi & Johnstone (2018), işlevsel sözcüklerin (1. tekil şahıs zamiri, mutlakiyetçi sözcükler) güçlü ve açıklanabilir belirteçler olduğunu gösterir.
4. **Sıfır sızıntı:** Ön işleme yalnızca eğitim katında (`Pipeline`), değerlendirme kişi bazlı gruplanmış ve zamansal bölmelerle, istatistiksel anlamlılık permütasyon testiyle sınanmalıdır.
5. **Doğruluk tek başına yasak:** Dengeli doğruluk, makro-F1, ROC-AUC, PR-AUC ve **kalibrasyon (Brier skoru)** birlikte raporlanmalıdır.
6. **Cinsiyet ve yaş adalet eksenidir:** Veriyi cinsiyete göre parçalayıp örneklem kaybetmek yerine tek model eğitilmeli, alt grup performans ve kalibrasyon farkları raporlanmalıdır.
7. **Tanı değil, güvenli yönlendirme:** Her tarama akışında PHQ-9 Madde 9 kriz güvenlik bayrağı, insan denetimi ve KVKK uyumlu rıza mekanizması zorunludur.
