# Veri Kartı (Datasheet): RHMCD-20

> Bu veri kartı, **Gebru vd. (2021)** *Datasheets for Datasets* (*Communications of the ACM*, 64(12), 86–92) çerçevesine uygun olarak, `mentalHealth/data.csv` ve `mentalHealth/dataTR.csv` dosyalarının şeffaf biçimde belgelenmesi için hazırlanmıştır.

---

## 1. Motivasyon

- **Veri setini kim, ne amaçla oluşturdu?**
  Imrus Salehin ve Nazrul Amin (Daffodil International University & Northern University Bangladesh; veri makalesinde ek yazarlar Md. Abu Baten ve Rabbi Al Noman). COVID-19 karantinası sırasında Bangladeş'teki bireylerin ruh sağlığı deneyimlerini yapılandırılmış bir anketle belgelemek ve makine öğrenmesi çalışmalarına girdi sağlamak amacıyla oluşturulmuştur.
- **Birincil kaynaklar:**
  - Veri deposu: Salehin, I., & Amin, N. (2023). *The RHMCD-20 datasets for Depression and Mental Health Data Analysis with Machine Learning* (V2). Mendeley Data. DOI: [10.17632/pxjmjyfdh2.2](https://doi.org/10.17632/pxjmjyfdh2.2)
  - Veri makalesi: Amin, N., Salehin, I., Baten, M. A., & Al Noman, R. (2024). *Data in Brief*, 54, 110376. DOI: [10.1016/j.dib.2024.110376](https://doi.org/10.1016/j.dib.2024.110376)
- **Lisans:** Mendeley Data üzerinde **CC BY 4.0** (atıf verilerek paylaşım ve uyarlama serbest). Veri makalesi **CC BY-NC 4.0**.

---

## 2. Bileşim (Composition)

- **Örnek birimi:** Her satır, ankete yanıt verdiği bildirilen bir bireyi temsil eder.
- **Boyut:** **824 satır × 13 sütun** (`mentalHealth/data.csv`). *(Not: Makalede 825 yanıt bildirilmiştir; CSV dosyasında başlık hariç 824 kayıt vardır.)*
- **Eksik değer ve tekrar:** CSV dosyasında `0` eksik hücre, `0` yinelenen satır bulunur.
- **Değişken türleri:** 13 sütunun **tamamı kategoriktir** (2 nominal, 11 sıralı/üçlü-ikili). Hiçbir sürekli ölçüm, zaman damgası, coğrafi koordinat veya standart klinik ölçek puanı yoktur.
- **Türkçe kopya (`mentalHealth/dataTR.csv`):** Aynı 824 satırın Türkçe etiketli karşılığıdır. Çeviri kusurları içerir:
  - `30-Above` → `30-` (belirsiz gösterim; doğru: `30 ve üzeri`)
  - `Occupation` → `Kurum` (yanlış; doğru: `Meslek`)
  - `Go out Every day` → `Her gün dışarı çık` (emir kipi; doğru: `Her gün dışarı çıkıyorum`)
  - `Female` → `Dişi` (insan anketinde `Kadın` tercih edilir)
  - `No` → `HAYIR` (tutarsız büyük harf)

---

## 3. Toplama Süreci (Collection Process)

- **Yer:** Dakka, Bangladeş (Khilgaon, Uttara ve Bashundhara yerleşim bölgeleri).
- **Kanal:** Çevrim içi ve yüz yüze yapılandırılmış anket.
- **Davet / yanıt oranı:** 1.000 davet, 825 yanıt (%82,5); %17,5 yanıtsız.
- **Eksik bilgiler:** Kesin veri toplama tarih aralığı (hangi karantina dalgası?), örnekleme yöntemi (olasılıklı mı, kolayda mı?), dışlama ölçütleri ve anketin pilot geçerlik/güvenirlik sonuçları makalede raporlanmamıştır.
- **Etik beyan:** Makalede Daffodil International University öğrenci araştırma kurulu onayı ve BMRC ilkelerine uyum ile bilgilendirilmiş onam alındığı belirtilmiştir.

---

## 4. Ön İşleme, Temizleme ve Bağımsız Kalite Denetimi

Veri makalesine göre eksik değerler **ortalama ile doldurma (mean imputation)** yöntemiyle kapatılmıştır — tamamen kategorik bir veri setinde ortalama doldurma yöntemsel olarak sorunludur.

Bu proje kapsamında [`src/mental_pulse/data.py`](../src/mental_pulse/data.py) ve [`mentalHealth/analiz_v2.ipynb`](../mentalHealth/analiz_v2.ipynb) ile yürütülen bağımsız kalite denetimi **dört kritik kırmızı bayrak** ortaya koymuştur:

| # | Denetim | Bulgu | Değerlendirme |
|---|---|---|---|
| **K1** | Dokümantasyon–CSV tutarlılığı | 13 sütundan **4'ünde** (`Mental_Health_History`, `Coping_Struggles`, `Work_Interest`, `Social_Weakness`) makaledeki Tablo 2 kategorileri ile CSV'deki gerçek kategoriler uyuşmuyor. | Yüksek risk — veri/dokümantasyon sürüm kayması. |
| **K2** | Tekdüzelik (uniformity) testi | 13 sütunun **13'ünde de** ki-kare uyum iyiliği testi $p \ge 0,05$ (ör. `Coping_Struggles` 414/410, $p = 0,889$; `Days_Indoors` $p = 0,881$). | Yüksek risk — gerçek klinik/toplum anketlerinde neredeyse görülmez. |
| **K3** | Değişkenler arası bağımlılık | 78 çiftin tamamında yanlılık düzeltmeli **Cramér's V ≤ 0,068**; BH-FDR sonrası anlamlı çift sayısı **0**. Uyku/beslenme değişimi ↔ kilo değişimi bile ilişkisiz ($p = 0,53$, $V = 0$). | Kritik — öğrenilebilir sinyal yok. |
| **K4** | Mantıksal tutarlılık | **89 satırda** `Gender = Male` ve `Occupation = Housewife`; **46 satırda** `Age = 16-20` ve `Occupation = Corporate`; meslek ile cinsiyet/yaş tamamen bağımsız ($V \approx 0$). | Kritik — ciddi veri toplama, karıştırma veya sentetik üretim şüphesi. |

---

## 5. Kullanım Alanları

### Uygun Kullanımlar
- **Yöntem eğitimi ve negatif kontrol:** Sızıntısız çapraz doğrulama, taban çizgisi karşılaştırması, Cramér's V ve permütasyon testinin *sinyal olmayan bir veride nasıl davrandığını* göstermek.
- **Kod ve metodoloji denetimi:** Yanlış ön işleme/SMOTE/üzerine yazma hatalarının nasıl yanıltıcı sonuçlar doğurduğunu öğretmek.

### Uygun Olmayan Kullanımlar (Önerilmez)
- **Klinik depresyon risk tahmini veya tarama aracı eğitimi** (geçerlenmiş klinik etiket ve istatistiksel sinyal yoktur).
- **Halk sağlığı politikası veya epidemiyolojik çıkarım** (Bangladeş'in genel nüfusunu temsil etmez; mantıksal tutarsızlıklar barındırır).
- **Türkiye popülasyonuna doğrudan genelleme** (farklı ülke, kültür ve pandemi dönemi).

---

## 6. Dağıtım ve Bakım

- Bu depoda orijinal dosyalar (`mentalHealth/data.csv` ve `mentalHealth/dataTR.csv`) değişiklik yapılmadan, yeniden üretilebilirlik amacıyla korunmuştur.
- Tüm yeni analizler İngilizce `data.csv` üzerinden yapılır; Türkçe karşılıklar yalnızca görselleştirme/raporlama katmanında eşlenir.
- Veri seti **donmuş (statik)** durumdadır; yeni sürümler için Mendeley Data DOI bağlantısı takip edilmelidir.
