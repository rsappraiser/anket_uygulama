import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass

# Gönderen ve alıcı bilgileri
from_email = "handegursoy@argedegerleme.com.tr"
to_email = "serdaredinsel@argedegerleme.com.tr"
password = getpass.getpass("Mail şifresini girin: ")

# Mail içeriği
subject = "Test Maili"
body = "Bu bir deneme mailidir."

# MIME yapısı
msg = MIMEMultipart()
msg["From"] = from_email
msg["To"] = to_email
msg["Subject"] = subject

msg.attach(MIMEText(body, "plain"))

# SMTP bağlantısı
try:
    server = smtplib.SMTP("mail.argedegerleme.com.tr", 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("✅ Mail başarıyla gönderildi.")
except Exception as e:
    print("❌ Hata oluştu:", e)