# Etik, Hukuk (KVKK) ve Klinik Güvenlik Çerçevesi

Ruh sağlığı verileri ve depresyon risk tahmin sistemleri, sıradan makine öğrenmesi uygulamalarından çok daha yüksek **hukuki, etik ve klinik zarar** riski taşır (Eichstaedt vd., 2018; Chancellor & De Choudhury, 2020; WHO, 2021). Bu belge, Mental Pulse'ın Faz 1–4 geliştirme ve araştırma süreçlerinde uyması gereken zorunlu kuralları tanımlar.

---

## 1. Hukuki Çerçeve: 6698 Sayılı KVKK ve GDPR

### 1.1 Sağlık verilerinin statüsü
- **6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) Madde 6** uyarınca *sağlık verileri* **özel nitelikli kişisel veridir**.
- **Kritik ayrım (Eichstaedt vd., 2018):** Bir kullanıcının sosyal medya gönderileri tek başına sağlık verisi olmasa bile, bunların üzerine depresyon riski çıkaran bir algoritma uygulandığında **üretilen çıkarım sağlık verisi niteliği kazanır** ve aynı korumaya tabi olur.
- Kişisel Verileri Koruma Kurulu'nun **31/01/2018 tarihli ve 2018/10 sayılı** *"Özel Nitelikli Kişisel Verilerin İşlenmesinde Veri Sorumlularınca Alınması Gereken Yeterli Önlemler"* kararı gereğince teknik ve idari tedbirler zorunludur.
- AB'de bulunan kullanıcı/katılımcılar için **GDPR Madde 9** (özel kategori veriler) ve yüksek riskli sağlık yapay zekâ sistemleri için **EU AI Act** şeffaflık/insan denetimi ilkeleri paralel olarak gözetilir.

### 1.2 Zorunlu teknik ve idari tedbirler (Mental Pulse kontrol listesi)
1. **Aydınlatma ve açık rıza:** Veri toplama öncesi anlaşılır Türkçe aydınlatma metni ve **ayrı, özgür iradeyle verilmiş, geri alınabilir açık rıza** (Madde 6).
2. **Veri minimizasyonu:** Yalnızca araştırma sorusu için gerekli alanlar toplanır; kimlik (ad, TCKN, kullanıcı adı, IP) ile araştırma verisi **ayrı tablolarda** tutulur.
3. **Takma adlandırma (Pseudonymization):** Katılımcı kimliği rastgele UUID ile eşlenir; eşleme anahtarı şifreli ve ayrı erişim yetkili kasada saklanır.
4. **Aktarımda ve depolamada şifreleme:** TLS 1.3 (aktarım) + AES-256 (depolama); veri dosyaları asla açık Git depolarına commit edilmez.
5. **Erişim denetimi ve loglama:** En az yetki ilkesi, çok faktörlü kimlik doğrulama, erişim kayıtlarının tutulması.
6. **Saklama süresi ve imha:** Araştırma bitiminde (veya katılımcı rızasını geri çektiğinde) kimlik-eşleme tablosu güvenli biçimde yok edilir; yalnızca anonimleştirilmiş istatistikler saklanır.
7. **Kazıma (scraping) yasağı:** Herkese açık sosyal medya profillerinin kullanıcı haberi olmadan taranıp ruh sağlığı profiline dönüştürülmesi **kesinlikle yasaktır**.

---

## 2. DSÖ (2021) Sağlıkta Yapay Zekâ Etiği İlkeleriyle Uyum

WHO (2021) *Ethics and Governance of Artificial Intelligence for Health* kılavuzundaki 6 ilkenin Mental Pulse'daki karşılığı:

| DSÖ İlkesi | Mental Pulse Uygulaması |
|---|---|
| **1. İnsan özerkliğini koruma** | Sistem asla otomatik tanı koymaz veya tedavi kararı almaz; nihai değerlendirme kullanıcı ve ruh sağlığı uzmanındadır. |
| **2. İnsan refahı ve güvenliği** | PHQ-9 Madde 9 kriz bayrağı (`screening.py`), yanlış-negatif/yanlış-pozitif zarar analizi, klinik eşik testleri. |
| **3. Şeffaflık, açıklanabilirlik ve anlaşılırlık** | TRIPOD+AI raporlaması, veri kartı, SHAP + psikolinguistik açıklamalar; başarısız/negatif sonuçların gizlenmemesi. |
| **4. Sorumluluk ve hesap verebilirlik** | Sürüm kontrollü kod, birim testleri, etik kurul onayı ve net sorumlu araştırmacı tanımı. |
| **5. Kapsayıcılık ve hakkaniyet** | Cinsiyet, yaş ve eğitim alt gruplarında ayrım (AUC) ve kalibrasyon (Brier) eşitliği denetimi (`subgroup_fairness_report`). |
| **6. Duyarlı ve sürdürülebilir YZ** | Hafif/açık modellerin öncelenmesi; gereksiz büyük model tüketiminden kaçınılması; kullanıcı geri bildirimiyle sürekli izlem. |

---

## 3. Klinik Güvenlik ve Kriz Müdahale Protokolü

Ruh sağlığı tarama araçlarında en ciddi güvenlik olayı **kendine zarar verme veya intihar düşüncesinin** bildirilmesidir.

### 3.1 PHQ-9 Madde 9 Tetikleyicisi
PHQ-9'un 9. maddesi (*"Ölmüş olsaydın daha iyi olacağı veya kendine bir şekilde zarar verme düşünceleri"*) **≥ 1** (bazı günler veya daha sık) olduğunda, toplam PHQ-9 puanı düşük olsa bile (`total_score < 10`), `mental_pulse.screening.score_phq9()` otomatik olarak `crisis_flag = True` döndürür ve acil destek bilgilerini ekler.

### 3.2 Zorunlu Kriz Yönlendirme Mesajı (Türkiye)
- **112 Acil Çağrı Merkezi** (7/24 acil sağlık ve kriz desteği)
- **ALO 183 Sosyal Destek Hattı** (7/24 psikososyal destek yönlendirmesi)
- **En yakın hastane acil servisi veya Psikiyatri / Ruh Sağlığı Polikliniği**
- Sistem arayüzünde **tanı koymama uyarısı** sabit ve görünür biçimde yer alır.

### 3.3 Yanlış Sınıflandırma Zarar Analizi

| Hata Türü | Olası Zarar | Azaltma Önlemi |
|---|---|---|
| **Yanlış Pozitif** (sağlıklı kişiye "yüksek risk") | Gereksiz kaygı, damgalanma, tıbbi kaynakların gereksiz meşgul edilmesi. | Olasılık yerine kalibre risk bandı + "tarama sonucu tanı değildir" açıklaması; yüksek eşikte ikinci aşama klinik ölçek. |
| **Yanlış Negatif** (gerçek depresyonun kaçırılması) | Yanlış güvence, yardım aramanın gecikmesi. | Yüksek duyarlılık odaklı tarama eşiği; "düşük skor rahatsızlığınız olmadığı anlamına gelmez" uyarısı. |

---

## 4. Araştırma Bilgilendirilmiş Onam Taslağı (Faz 1–3 İçin Şablon)

> *Bu şablon, üniversite Sosyal ve Beşerî Bilimler / Tıp Etiği Kurulu başvurusunda temel alınmak üzere hazırlanmıştır; hukuk ve etik kurul incelemesinden geçmeden sahada kullanılmamalıdır.*

1. **Çalışmanın adı ve amacı:** Mental Pulse kapsamında depresif belirtilerin erken taranmasına yönelik istatistiksel/yapay zekâ modellerinin geliştirilmesi.
2. **Ne toplanacak?** (a) PHQ-9 ve GAD-7 anket yanıtları, (b) temel demografi (yaş aralığı, cinsiyet, eğitim, meslek, sosyal destek), (c) varsa gönüllü olarak paylaşılan metin örnekleri veya pasif hareketlilik özetleri.
3. **Gönüllülük ve çekilme hakkı:** Katılım tamamen gönüllüdür; hiçbir gerekçe göstermeden istediğiniz an çekilebilir ve verilerinizin silinmesini talep edebilirsiniz.
4. **Gizlilik:** Yanıtlarınız kimliğinizden ayrılarak rastgele bir kodla saklanacaktır; sonuçlar yalnızca toplulaştırılmış bilimsel yayınlarda paylaşılacaktır.
5. **Tıbbi uyarı:** Bu çalışma tanı veya tedavi sunmaz. Çalışma sırasında kendinizi bunalmış hissederseniz 112'yi arayabilir veya bir ruh sağlığı uzmanına başvurabilirsiniz.
6. **İletişim ve sorumlu araştırmacı:** [Kurum / Danışman / Etik Kurul Onay Numarası eklenecektir.]
