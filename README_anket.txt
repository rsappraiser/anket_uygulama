
Arge Gayrimenkul Değerleme ve Danışmanlık A.Ş. Anket Uygulaması – README

1. Proje Hakkında
Bu uygulama, Arge Gayrimenkul Değerleme ve Danışmanlık A.Ş. çalışanlarının birimler ve personel için değerlendirme yapabileceği bir anket uygulamasıdır.
Katılımcı erişimi token bazlı güvenlik ile sağlanmaktadır.

2. Kullanılan Teknolojiler
- Python (3.10+)
- Streamlit (web arayüzü için)
- Pandas (veri işlemleri için)
- Excel (.xlsx) dosya kaydı
- JSON (geçici veri kaydı)

3. Gereksinimler
- Python 3.10 veya üstü yüklü olmalı.
- Gerekli Python kütüphaneleri:
    pip install streamlit pandas openpyxl
- Dosya okuma/yazma yetkisi olmalı.

4. Dosya ve Klasör Yapısı
- anket_app.py → Ana uygulama kodu
- Kullanici_Listesi_Tokenli.xlsx → Token bazlı kullanıcı listesi
- Birim_Degerlendirme_Anketi_Guncel.xlsx → Anket soruları
- /anket_sonuclari/ → Anket cevaplarının Excel dosyaları
- /temp_cevaplar/ → Geçici JSON dosyaları

5. Kurulum ve Çalıştırma
- Proje dosyalarını sunucuya aktarın.
- Gerekli kütüphaneleri yükleyin.
- Aşağıdaki komutla çalıştırın:
    streamlit run anket_app.py
- 8501 portu açık olmalı.
- Kullanıcılar link ile giriş yapacak (örnek domain anket.argedegerleme.com.tr olacak şekilde);
  https://anket.argedegerleme.com.tr/?token=TOKENDEGERI

6. Kaydedilen Veriler
- Excel dosyaları /anket_sonuclari/ klasörüne yazılır.
- Geçici kayıtlar /temp_cevaplar/ klasöründe tutulur.

7. Önemli Notlar
- Uygulama şimdilik dosya bazlı çalışmakta ve veriler local klasör içine kaydedilmekte (veritabanı entegrasyonu yapılmamış).
- Admin paneli yoktur, gerekirse ayrıca geliştirilebilir.

8. İletişim
- Hande EDİNSEL 530 066 9468 İç Denetim Müdürü

Örnek Tokenlı URL:
https://anket.argedegerleme.com.tr/?token=91cb325eaf3c42879347f7f55f0bc7c8
