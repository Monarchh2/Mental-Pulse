# TRIPOD+AI Öz-Değerlendirme Kontrol Listesi

> **Referans:** Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L., Van Calster, B., ... & Logullo, P. (2024). *TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods.* **BMJ**, 385, e078378.
>
> **Amaç:** Mental Pulse projesinin **orijinal hâli (v1 — `analiz.ipynb`)**, **gözden geçirilmiş mevcut hâli (v2 — `analiz_v2.ipynb` + `src/mental_pulse`)** ve **planlanan klinik/NLP sürümü (v3 — Faz 1–4)** arasındaki metodolojik olgunluk farkını şeffaf biçimde ortaya koymak.

**Durum Göstergeleri:** ✔ Karşılandı · ◐ Kısmen · ✘ Eksik / Hatalı · 🎯 Faz 1–4 hedefi

| Madde | Bölüm | TRIPOD+AI Gereksinimi (Özet) | v1 (`analiz.ipynb`) | v2 (Mevcut) | v3 (Hedef) | Açıklama / Depodaki Karşılık |
|---|---|---|---|---|---|---|
| 1 | Başlık | Çalışmanın tahmin modeli geliştirme/doğrulama olduğunu ve hedefi belirt | ✘ | ✔ | 🎯 | `README.md` ve `docs/ARASTIRMA_RAPORU.md` başlıkları netleştirildi. |
| 2 | Özet | Yapılandırılmış özet (amaç, veri, yöntem, temel bulgular) | ◐ | ✔ | 🎯 | `ARASTIRMA_RAPORU.md §1` Yönetici Özeti. |
| 3a–b | Giriş | Klinik/halk sağlığı gerekçesi ve açık amaçlar | ◐ | ✔ | 🎯 | DSÖ (2026), Lancet (2021), TÜİK/Yıldız vd. (2024) ile temellendirildi. |
| 4 | Yöntem: Veri kaynağı | Veri kaynağını, toplama tarihlerini ve çalışmanın tasarımını tanımla | ✘ | ✔ | 🎯 | RHMCD-20 künyesi, Mendeley DOI ve `VERI_KARTI_RHMCD20.md` eklendi. |
| 5a–c | Katılımcılar | Katılım/dışlama ölçütleri, ortam, demografik özellikler | ✘ | ◐ | 🎯 | RHMCD-20 makalesinden aktarılabilenler belgelendi; eksik detaylar kısıt olarak yazıldı. |
| 6a–b | Sonuç (Outcome) | Hedef değişkenin açık tanımı ve kör ölçümü | ✘ | ✔ | 🎯 | v2'de `Social_Weakness`'ın klinik depresyon olmadığı açıkça raporlandı; v3'te PHQ-9 ≥ 10 (`screening.py`). |
| 7 | Öngörücüler | Tüm aday özelliklerin tanımı ve kodlama stratejisi | ✘ | ✔ | 🎯 | `data.py` (`ORDINAL_ORDERS`, `NOMINAL_COLUMNS`) ve veri sözlüğü. |
| 8 | Örneklem büyüklüğü | Örneklem büyüklüğünün gerekçelendirilmesi (olay sayısı / parametre oranı) | ✘ | ◐ | 🎯 | v2'de n = 824 kısıt olarak irdelendi; v3'te veri toplama öncesi güç/EPV hesabı zorunlu. |
| 9a–c | Eksik veri | Eksik verilerin raporlanması ve ele alınması | ◐ | ✔ | 🎯 | CSV'de 0 eksik olduğu doğrulandı; orijinal makaledeki ortalama doldurma eleştirildi. |
| 10a–b | Veri hazırlığı / Ön işleme | Özellik dönüşümü, ölçekleme, yeniden örnekleme ve **sızıntı önleme** | ✘ | ✔ | 🎯 | v1'de SMOTE üzerine yazma + alfabetik `LabelEncoder` vardı. v2'de tüm adımlar `Pipeline` içinde. |
| 11 | Model belirleme | Aday algoritmalar, hiperparametreler ve taban çizgileri | ◐ | ✔ | 🎯 | `modeling.py`: 2 `DummyClassifier` + 5 sınıflandırıcı, sabit `random_state`. |
| 12 | Performans ölçütleri | Ayrım (ROC-AUC), sınıflandırma, **kalibrasyon (Brier/eğri)** | ✘ | ✔ | 🎯 | v1 yalnızca ham doğruluk ve yanlış adlandırılmış "Tahmin" (precision) veriyordu. v2: dengeli doğruluk, makro-F1, ROC-AUC, Brier. |
| 13 | Yeniden örnekleme / Doğrulama | İç geçerleme (tekrarlı CV) ve varsa dış geçerleme | ✘ | ✔ (İç) | 🎯 (Dış) | v2'de 5×3 / 5×5 tekrarlı tabakalı CV + 200 permütasyon testi; v3'te kişi bazlı + zamansal + dış geçerleme. |
| 14 | Adalet (Fairness) | Demografik alt gruplarda performans/kalibrasyon farklılıkları | ✘ | ✔ | 🎯 | `subgroup_fairness_report()` cinsiyet ve yaş kırılımlarını raporlar. |
| 15 | Güncelleme / Yeniden kalibrasyon | Dış doğrulamada model güncelleme stratejisi | ✘ | — | 🎯 | Faz 3–4'te dış kohort üzerinde yeniden kalibrasyon planlandı. |
| 16 | Hasta/halk katılımı | Hedef kullanıcı ve klinisyenlerin tasarıma katılımı | ✘ | ◐ | 🎯 | Faz 4'te uzman psikiyatri/psikoloji paneli ve kullanıcı testi tanımlandı. |
| 17 | Etik ve rıza | Etik kurul onayı, veri gizliliği, hukuki dayanak | ✘ | ✔ | 🎯 | `docs/ETIK_VE_KVKK_CERCEVESI.md` (KVKK Md. 6 + WHO 2021). |
| 18 | Sonuçlar: Katılımcı akışı | Veri boyutları, alt grup dağılımları ve kalite denetimi | ◐ | ✔ | 🎯 | `run_full_audit()` + `01_dagilimlar.png` + `04_mantiksal_tutarlilik.png`. |
| 19 | Model geliştirme sonuçları | Tüm modellerin tablo/grafik sonuçları ve belirsizlik (SS / GA) | ✘ | ✔ | 🎯 | CV ort ± SS + permütasyon p-değeri + `05_model_kiyaslama.png`. |
| 20 | Model performansı | Taban çizgisine göre kazanç ve negatif sonuçların dürüst bildirimi | ✘ | ✔ | 🎯 | Şans düzeyinde kalma açıkça raporlandı (negatif bulgu şeffaflığı). |
| 21 | Açıklanabilirlik | Özellik önemleri / yerel açıklamalar (SHAP vb.) | ✘ | ◐ | 🎯 | v2'de sinyal olmadığı için özellik önemi yorumlanmadı (yanıltıcı olurdu); v3'te SHAP + psikolinguistik özellikler zorunlu. |
| 22 | Tartışma: Yorum | Bulguların literatürle karşılaştırılması | ✘ | ✔ | 🎯 | `ARASTIRMA_RAPORU.md §8` ve `LITERATUR_MATRISI.md`. |
| 23 | Kısıtlar | Veri, örneklem, ölçüm ve genellenebilirlik kısıtları | ◐ | ✔ | 🎯 | 10 başlıkta genişletilmiş kısıt ve risk matrisi (`ARASTIRMA_RAPORU.md §14`). |
| 24 | Kullanılabilirlik / Klinik çıkarım | Tanı değil tarama vurgusu; hata maliyetleri; kriz protokolü | ✘ | ✔ | 🎯 | `screening.py` içinde PHQ-9 Madde 9 kriz güvenlik bayrağı + 112/ALO 183. |
| 25 | Açık bilim: Kod ve veri | Yeniden üretilebilir kod, ortam dosyası, testler | ◐ | ✔ | 🎯 | `src/mental_pulse/`, `tests/`, `pyproject.toml`, `requirements.txt`, `analiz_v2.ipynb`. |
| 26 | Çıkar çatışması / Fon | Finansman ve çıkar çatışması beyanı | ✘ | ✔ | 🎯 | Akademik/açık kaynak araştırma projesi; ticari çıkar çatışması yoktur. |
| 27 | Protokol / Ön kayıt | Araştırma protokolünün önceden kaydedilmesi (OSF vb.) | ✘ | ◐ | 🎯 | Faz 1 veri toplama öncesi OSF ön kaydı önerilir. |

---

### Özet Skor

| Sürüm | ✔ Karşılanan | ◐ Kısmen | ✘ Eksik |
|---|---|---|---|
| **v1 (orijinal depo)** | 0 / 27 | 7 / 27 | 20 / 27 |
| **v2 (bu güncelleme)** | **21 / 27** | **5 / 27** | **0 / 27** *(1 madde dış doğrulama için N/A)* |
| **v3 (Faz 1–4 sonrası hedef)** | **27 / 27** | 0 | 0 |
