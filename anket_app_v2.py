import streamlit as st
st.set_page_config(layout="wide", page_title="Arge Gayrimenkul Değerleme ve Danışmanlık A.Ş. Anket Uygulaması")
import pandas as pd
import base64
import os
import json
import time
start_time = time.time()
print("📌 [LOG] Kod başlatıldı")
st.write("⏳ Uygulama başlatılıyor...")
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# --- Yardımcı Fonksiyonlar ---
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def kaydet_cevaplar(ad_soyad, birim, cevaplar_birim):
    os.makedirs("anket_sonuclari", exist_ok=True)
    filename = f"anket_sonuclari/sonuc_{ad_soyad.replace(' ','_').lower()}.xlsx"
    cevaplar_birim["Birim"] = birim

    if os.path.exists(filename):
        mevcut_df = pd.read_excel(filename)
        mevcut_df = mevcut_df[mevcut_df["Birim"] != birim]
    else:
        mevcut_df = pd.DataFrame()

    yeni_df = pd.DataFrame([cevaplar_birim])
    sonuc_df = pd.concat([mevcut_df, yeni_df], ignore_index=True)
    sonuc_df.to_excel(filename, index=False)
    os.makedirs("/mount/src/anket_sonuclari", exist_ok=True)
    sonuc_df.to_excel("/mount/src/anket_sonuclari/sonuc_{}.xlsx".format(ad_soyad.replace(' ','_').lower()), index=False)

    # Google Drive'a yükleme
    import sys
    print("✅ googleapiclient modülü kontrol ediliyor...", file=sys.stderr)
    try:
        import googleapiclient
        print("✅ googleapiclient modülü yüklü.", file=sys.stderr)
    except ImportError:
        print("❌ googleapiclient modülü bulunamadı!", file=sys.stderr)
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        key_data = dict(st.secrets["google"])
        key_data["private_key"] = base64.b64decode(st.secrets["google"]["private_key_b64"])

        drive_creds = service_account.Credentials.from_service_account_info(
            key_data,
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        drive_service = build("drive", "v3", credentials=drive_creds)

        file_metadata = {"name": os.path.basename(filename)}
        media = MediaFileUpload(filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    except Exception as e:
        print("Google Drive'a yükleme hatası:", e)

    # Google Sheets'e kaydetme
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google"], scope)
        client = gspread.authorize(creds)

        sheet_name = "Anket_Sonuclari"
        spreadsheet = None
        try:
            spreadsheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(sheet_name)
            spreadsheet.share('', perm_type='anyone', role='writer')

        worksheet_title = ad_soyad.replace(' ', '_')
        try:
            worksheet = spreadsheet.worksheet(worksheet_title)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols="20")

        worksheet.update([sonuc_df.columns.values.tolist()] + sonuc_df.values.tolist())

    except Exception as e:
        print("Google Sheets'e kaydetme hatası:", e)

def kaydet_temp_cevaplar(ad_soyad, cevaplar):
    print(f"🟢 [TRACE] Temp cevap kaydı başlıyor: {ad_soyad}")
    print(f"🔍 [DEBUG] kaydet_temp_cevaplar başlatıldı - Kullanıcı: {ad_soyad}")
    print("💡 kaydet_temp_cevaplar fonksiyonu çağrıldı")
    os.makedirs("temp_cevaplar", exist_ok=True)
    temp_file = f"temp_cevaplar/temp_{ad_soyad.replace(' ','_').lower()}.json"
    print(f"📝 [LOG] Geçici cevap kaydediliyor: {temp_file}")
    st.write("📄 Geçici cevap kaydediliyor...")
    print(f"🟢 [TRACE] Dosya hazırlanıyor: {temp_file}")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(cevaplar, f, ensure_ascii=False, indent=2)
        print(f"🟢 [TRACE] JSON dump tamamlandı: {temp_file}")
    print(f"✅ [LOG] Geçici cevap dosyası yazıldı: {temp_file}")

    # Google Drive'a geçici cevap yükleme
    print(f"📤 [LOG] Google Drive'a geçici cevap yükleme başlıyor: {temp_file}")
    st.write("📤 Google Drive'a yükleniyor...")
    print("🟢 [TRACE] Google upload aşaması başladı")
    import sys
    print("✅ googleapiclient modülü kontrol ediliyor...", file=sys.stderr)
    try:
        import googleapiclient
        print("✅ googleapiclient modülü yüklü.", file=sys.stderr)
    except ImportError:
        print("❌ googleapiclient modülü bulunamadı!", file=sys.stderr)
    try:
        print("🔐 [DEBUG] st.secrets.keys():", list(st.secrets.keys()))
        print(f"📤 [DEBUG] Google Drive upload için hazırlanıyor: {temp_file}")
        # --- DEBUG prints for private_key_b64 ---
        print("🧪 [DEBUG] private_key_b64 mevcut mu?:", "private_key_b64" in st.secrets["google"])
        print("🧪 [DEBUG] private_key_b64 ilk 50 karakter:", st.secrets["google"].get("private_key_b64", "")[:50])
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        import base64
        key_data = dict(st.secrets["google"])
        key_data["private_key"] = base64.b64decode(st.secrets["google"]["private_key_b64"])

        drive_creds = service_account.Credentials.from_service_account_info(
            key_data,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=drive_creds)

        file_metadata = {"name": os.path.basename(temp_file)}
        media = MediaFileUpload(temp_file, mimetype="application/json")
        response = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"✅ [LOG] Geçici cevap Google Drive'a yüklendi. Dosya ID: {response.get('id')}")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("❌ [DEBUG] Google Drive yükleme kısmında hata oluştu:\n", tb)
        print(f"❌ [LOG] Geçici cevap Google Drive'a yüklenemedi: {e}")

def yukle_temp_cevaplar(ad_soyad):
    temp_file = f"temp_cevaplar/temp_{ad_soyad.replace(' ','_').lower()}.json"
    if os.path.exists(temp_file):
        with open(temp_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sil_temp_cevaplar(ad_soyad):
    temp_file = f"temp_cevaplar/temp_{ad_soyad.replace(' ','_').lower()}.json"
    if os.path.exists(temp_file):
        os.remove(temp_file)

# --- Yeni: Token Kullanım Kontrol Fonksiyonları ---
def kaydet_token(token):
    os.makedirs("kullanilan_tokenler", exist_ok=True)
    path = "kullanilan_tokenler/kullanilan_tokenler.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            tokenler = json.load(f)
    else:
        tokenler = []

    if token not in tokenler:
        tokenler.append(token)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(tokenler, f, ensure_ascii=False, indent=2)

def kontrol_token(token):
    path = "kullanilan_tokenler/kullanilan_tokenler.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            tokenler = json.load(f)
        return token in tokenler
    return False

# --- Oturum Başlat ---
for key, value in {
    "ankete_basla": False,
    "secilen_ad": "",
    "secilen_birim": "",
    "cevaplar": {},
    "cevaplanan_birimler": [],
    "anket_tamamlandi": False,
    "bitirme_onayi": False,
    "sorulari_goster": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

aktif_banner = get_base64_image("anket_wallpaper.png") if st.session_state["ankete_basla"] else get_base64_image("lastwallpaper.png")

# --- CSS ---
st.markdown(f"""<style>
.banner {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 200px;
    background-image: url('data:image/png;base64,{aktif_banner}');
    background-size: cover;
    background-position: top left;
    background-repeat: no-repeat;
    z-index: 998;
}}
.content {{
    margin-top:240px;
    padding-left: 5rem;
    padding-right: 5rem;
}}
div.stButton > button {{
    height: 3em;
    width: 100%;
    border-radius: 10px;
    transition: 0.3s;
    font-weight: bold;
}}
div.stButton > button:hover {{
    transform: scale(1.05);
    background-color: #FFCCCB;
}}
div.stButton > button:has(svg) {{
    margin-top: -20px;
}}
.block-container .stSelectbox {{
    /* margin-top: 10px; */
}}
label[for^="Değerlendirmek istediğiniz birimi seçiniz"] {{
    margin-top: 20px !important;
    display: block;
}}
div[data-baseweb="select"] {{
    margin-top: -10px;
}}
div[data-testid="column"] {{
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.5rem;
    margin-bottom: 0.5rem;
}}
</style><div class='banner'></div><div class='content'>""", unsafe_allow_html=True)

# --- Kullanıcı Listesi ---
import os
excel_path = os.path.join(os.path.dirname(__file__), "Kullanici_Listesi_Tokenli.xlsx")
kullanicilar_df = pd.read_excel(excel_path)
print("✅ [LOG] Kullanıcı Excel yüklendi. Geçen süre:", round(time.time() - start_time, 2), "saniye")

# --- Token Oku ---
if "token" not in st.session_state:
    token = st.query_params.get("token", None)
    if isinstance(token, list):
        token = token[0]
    st.session_state["token"] = token

# --- Giriş Sayfası ---
if not st.session_state["ankete_basla"] and not st.session_state["anket_tamamlandi"]:
    print("📋 [LOG] Giriş sayfası yüklendi. Süre:", round(time.time() - start_time, 2), "saniye")
    token = st.session_state["token"]

    if token and kontrol_token(token):
        st.error("Bu anketi daha önce tamamlamıştınız. Sayfadan çıkış yapabilirsiniz.")
        st.stop()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="typewriter"><h1>Hoş Geldiniz</h1></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-text">
        Bu anket, şirketimizdeki Muhasebe, Operasyon, Denetim birimlerinin ve yöneticilerin değerlendirilmesi amacıyla hazırlanmıştır.<br>
        <br>Görüşleriniz bizim için değerlidir. Lütfen birimlere ve çalışanlara, <b>kişisel görüşlerden bağımsız, sadece iş performansı ve gözlemleriniz doğrultusunda </b> 1 (kesinlikle katılmıyorum), 2 (katılmıyorum), 3 (fikrim yok), 4 (katılıyorum), 5 (kesinlikle katılıyorum) olacak şekilde puan veriniz.
        Eğer bir çalışan hakkında değerlendirme yapacak kadar fikriniz olmadığını düşünüyorsanız "3 (Fikrim Yok)" seçeneğini kullanabilirsiniz.<br><br>
        İş birliğiniz için teşekkür ederiz.<br><br><b>İÇ DENETİM BİRİMİ</b>

        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown("## Anket Girişi")
            if token and token in kullanicilar_df["token"].astype(str).values:
                ad_soyad = kullanicilar_df[kullanicilar_df["token"].astype(str) == token]["Adı Soyadı"].values[0]
                st.session_state["secilen_ad"] = ad_soyad
                st.markdown(f"Sayın **{ad_soyad}**, ankete başlamak için aşağıdaki butona tıklayınız.", unsafe_allow_html=True)
                if st.button("Ankete Başla"):
                    print("🟡 [LOG] Ankete Başla butonuna basıldı.")
                    st.session_state["cevaplar"] = yukle_temp_cevaplar(ad_soyad)
                    print("📁 [LOG] Geçici cevaplar yüklendi. Süre:", round(time.time() - start_time, 2), "saniye")
                    st.session_state["ankete_basla"] = True
                    st.session_state["bitirme_onayi"] = False
                    st.rerun()
            else:
                st.error("Geçersiz veya kullanılmış token. Doğru linki kullandığınızdan emin olun.")

elif st.session_state["anket_tamamlandi"]:
    st.balloons()
    st.markdown("<h2 style='text-align: center;'>🎉 Teşekkürler! Anketi tamamladınız. 🎉</h2>", unsafe_allow_html=True)
    sil_temp_cevaplar(st.session_state["secilen_ad"])

# Anket Sayfası

if st.session_state["ankete_basla"]:
    calisanlar = {
        "Muhasebe": [" "],
        "Operasyon": ["Beyza Karaer (TAKBİS)", "Can Akyürek", "Gözde Tokgözoğlu", "Nihan Soran", "Tuğba Tenbel"],
        "Denetim": ["Arzu Acar Düzenli", "Bahadır Alten", "Burhan Berk Taner", "Canan Göker",
                    "Derya Zengin", "Gökçe Millici Nakkaş", "Mehmet Sofi", "Özge Çakır", "Pınar Yıldırım",
                    "Selçuk Avlar", "Simge Demir"],
        "Birim Yöneticileri": ["Serdar Edinsel (Genel Müdür Yardımcısı)", "İrfan Çakmak (Operasyon Birimi Müdürü)", "Aysel Özcan (İK ve İş Geliştirme Müdürü)", "Betül Aksoy (Bordro ve Personel İşleri Yöneticisi)"],
        "Yönetim Kurulu": [" "],
        "Sosyal Yaşam ve Teknoloji": [" "],
        "Görüş ve Öneriler": []
    }

    try:
        dan_df = pd.read_excel("Birim_Degerlendirme_Anketi_Guncel.xlsx")
    except Exception:
        dan_df = pd.DataFrame()
    # -- Kontrol: dan_df boş veya gerekli sütunlar yoksa hata ver ve dur --
    if dan_df.empty or "Birim" not in dan_df.columns or "Soru" not in dan_df.columns:
        st.error("Anket soruları yüklenemedi. Excel dosyası eksik veya hatalı.")
        st.stop()

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("🔙 Geri"):
            st.session_state["ankete_basla"] = False
            st.rerun()

    birim = st.selectbox("Değerlendirmek istediğiniz birimi seçiniz", options=list(calisanlar.keys()))

    if birim != st.session_state.get("secilen_birim", ""):
        st.session_state["secilen_birim"] = birim
        st.session_state["sorulari_goster"] = False
        st.rerun()

    if st.button("Soruları Getir"):
        st.session_state["sorulari_goster"] = True

    if st.session_state.get("sorulari_goster", False):
        secilen_birim = st.session_state["secilen_birim"]

        if secilen_birim == "Görüş ve Öneriler":
            st.subheader("Görüş ve Öneriler")
            oneri_key = f"oneri_gorus_{st.session_state['secilen_ad']}"
            mevcut_yanit = st.session_state["cevaplar"].get("Görüş ve Öneriler", {}).get(oneri_key, "")
            kullanici_yanit = st.text_area("Tüm birimler ile ilgili iletmek istediğiniz görüş ve önerileriniz varsa aşağıda paylaşabilirsiniz.", value=mevcut_yanit, height=200)

            if "Görüş ve Öneriler" not in st.session_state["cevaplar"]:
                st.session_state["cevaplar"]["Görüş ve Öneriler"] = {}

            st.session_state["cevaplar"]["Görüş ve Öneriler"][oneri_key] = kullanici_yanit
            kaydet_temp_cevaplar(st.session_state["secilen_ad"], st.session_state["cevaplar"])

            if "oneri_bitirme_onayi" not in st.session_state:
                st.session_state["oneri_bitirme_onayi"] = False

            if not st.session_state["oneri_bitirme_onayi"]:
                if st.button("Görüş ve Önerileri Kaydet ve Anketi Bitir"):
                    # Önce tüm zorunlu birimler tamamlandı mı kontrol et
                    eksik_birimler = []
                    for birim in calisanlar.keys():
                        if birim in ["Görüş ve Öneriler"]:
                            continue
                        birim_sorular = dan_df[dan_df["Birim"] == birim]["Soru"].tolist()
                        for soru in birim_sorular:
                            for kisi in calisanlar[birim]:
                                key = f"{birim}_{soru}_{kisi}_{st.session_state['secilen_ad']}"
                                if st.session_state["cevaplar"].get(birim, {}).get(key, "Seçiniz") == "Seçiniz":
                                    eksik_birimler.append(birim)
                                    break

                    if eksik_birimler:
                        st.warning(f"Lütfen tüm birimler için anketi tamamlayınız. Eksik: {', '.join(set(eksik_birimler))}")
                    else:
                        st.session_state["oneri_bitirme_onayi"] = True
                        st.rerun()
            else:
                st.warning("Bu işlemi tamamladıktan sonra cevaplarınızı değiştiremezsiniz. Emin misiniz?")
                col1, col2 = st.columns([0.3, 0.7])
                with col1:
                    if st.button("✅ Evet, Anketi Tamamla"):
                        kaydet_cevaplar(st.session_state["secilen_ad"], "Görüş ve Öneriler", {oneri_key: kullanici_yanit})
                        kaydet_token(st.session_state["token"])
                        st.session_state["cevaplanan_birimler"].append("Görüş ve Öneriler")
                        sil_temp_cevaplar(st.session_state["secilen_ad"])
                        st.session_state["anket_tamamlandi"] = True
                        st.session_state["ankete_basla"] = False
                        st.rerun()
                with col2:
                    if st.button("❌ Vazgeç"):
                        st.session_state["oneri_bitirme_onayi"] = False
                        st.rerun()
            st.stop()

        sorular = dan_df[dan_df["Birim"] == secilen_birim]["Soru"].tolist()
        if not sorular:
            st.warning(f"{secilen_birim} birimi için tanımlı soru bulunamadı.")
            st.stop()

        st.subheader(f"{secilen_birim} Anket Soruları")

        if secilen_birim not in st.session_state["cevaplar"]:
            st.session_state["cevaplar"][secilen_birim] = {}

        if not calisanlar.get(secilen_birim):
            st.error(f"{secilen_birim} birimi için tanımlı çalışan bulunamadı.")
            st.stop()
        cols = st.columns(len(calisanlar[secilen_birim]) + 1)
        cols[0].markdown("** **", unsafe_allow_html=True)

        # st.markdown("""
        # <style>
        # .block-container .stSelectbox {
        #     margin-top: -35px;
        # }
        # </style>
        # """, unsafe_allow_html=True)

        for i, kisi in enumerate(calisanlar[secilen_birim]):
            cols[i+1].markdown(f"**{kisi}**")

        for idx, soru in enumerate(sorular, 1):
            row = st.columns(len(calisanlar[secilen_birim]) + 1)
            row[0].markdown(f"{idx}. {soru}")

            for j, kisi in enumerate(calisanlar[secilen_birim]):
                key = f"{secilen_birim}_{soru}_{kisi}_{st.session_state['secilen_ad']}"
                onceki_secim = st.session_state["cevaplar"][secilen_birim].get(key, "Seçiniz")
                secim = row[j+1].selectbox("", ["Seçiniz", 1, 2, 3, 4, 5],
                                           key=key,
                                           index=["Seçiniz", 1, 2, 3, 4, 5].index(onceki_secim))
                st.session_state["cevaplar"][secilen_birim][key] = secim

        kaydet_temp_cevaplar(st.session_state["secilen_ad"], st.session_state["cevaplar"])

        if secilen_birim == list(calisanlar.keys())[-1]:  # Only after last section
            st.subheader("💭 Öneri ve Görüşler")
            oneri_key = f"oneri_gorus_{st.session_state['secilen_ad']}"
            mevcut_yanit = st.session_state["cevaplar"].get("OneriVeGorusler", {}).get(oneri_key, "")
            kullanici_yanit = st.text_area("Anketle ilgili genel görüşlerinizi ve önerilerinizi buraya yazabilirsiniz:", value=mevcut_yanit, height=200)

            if "OneriVeGorusler" not in st.session_state["cevaplar"]:
                st.session_state["cevaplar"]["OneriVeGorusler"] = {}

            st.session_state["cevaplar"]["OneriVeGorusler"][oneri_key] = kullanici_yanit
            kaydet_temp_cevaplar(st.session_state["secilen_ad"], st.session_state["cevaplar"])

        if st.button(f"{secilen_birim} Cevaplarını Kaydet"):
            cevaplar_birim = st.session_state["cevaplar"].get(secilen_birim, {})

            eksik_sorular = set()
            for idx, soru in enumerate(sorular, 1):
                for kisi in calisanlar[secilen_birim]:
                    key = f"{secilen_birim}_{soru}_{kisi}_{st.session_state['secilen_ad']}"
                    if st.session_state["cevaplar"][secilen_birim].get(key, "Seçiniz") == "Seçiniz":
                        eksik_sorular.add(idx)

            if eksik_sorular:
                eksikler = sorted(list(eksik_sorular))
                st.warning(f"🚨 Eksik cevapladığınız soru numaraları: {', '.join(map(str, eksikler))}")
            else:
                kaydet_cevaplar(st.session_state["secilen_ad"], secilen_birim, cevaplar_birim)
                if secilen_birim not in st.session_state["cevaplanan_birimler"]:
                    st.session_state["cevaplanan_birimler"].append(secilen_birim)
                st.success(f"{secilen_birim} Birimi için cevaplarınız kaydedildi. Bir sonraki birime geçiniz.")
                kaydet_temp_cevaplar(st.session_state["secilen_ad"], st.session_state["cevaplar"])

        # Anketi Bitirme
        cevaplanan_birimler = []
        for birim in calisanlar.keys():
            if birim not in st.session_state["cevaplar"]:
                continue
            if birim == "Görüş ve Öneriler":
                continue
            birim_sorular = dan_df[dan_df["Birim"] == birim]["Soru"].tolist()
            tum_cevaplandi = True
            for soru in birim_sorular:
                for kisi in calisanlar[birim]:
                    key = f"{birim}_{soru}_{kisi}_{st.session_state['secilen_ad']}"
                    if st.session_state["cevaplar"].get(birim, {}).get(key, "Seçiniz") == "Seçiniz":
                        tum_cevaplandi = False
            if tum_cevaplandi:
                cevaplanan_birimler.append(birim)
        eksik_birimler = [b for b in calisanlar.keys() if b not in cevaplanan_birimler and b != "Görüş ve Öneriler"]

        if not eksik_birimler:
            if not st.session_state["bitirme_onayi"]:
                if st.button("Anketi Bitir"):
                    st.session_state["bitirme_onayi"] = True
                    st.rerun()
            else:
                st.warning("Bu işlemi tamamladıktan sonra cevaplarınızı değiştiremezsiniz. Emin misiniz?")
                col1, col2 = st.columns([0.3, 0.7])
                with col1:
                    if st.button("✅ Evet, Anketi Tamamla"):
                        kaydet_token(st.session_state["token"])
                        with st.spinner("Anket tamamlanıyor..."):
                            time.sleep(2)
                        st.session_state["anket_tamamlandi"] = True
                        st.session_state["ankete_basla"] = False
                        st.rerun()
                with col2:
                    if st.button("❌ Vazgeç"):
                        st.session_state["bitirme_onayi"] = False
                        st.rerun()

