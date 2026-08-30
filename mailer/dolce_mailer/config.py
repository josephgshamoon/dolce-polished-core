import os
from dotenv import load_dotenv

load_dotenv()

WIX_API_KEY = os.environ.get("WIX_API_KEY", "")
WIX_SITE_ID = os.environ.get("WIX_SITE_ID", "")
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8080").rstrip("/")
APPROVER_EMAIL = os.environ.get("APPROVER_EMAIL", "dolce.erbil@gmail.com")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "hello@dolceclinic.com")
FROM_NAME = os.environ.get("FROM_NAME", "Dolce Aesthetic Clinic")
DB_PATH = os.environ.get("DB_PATH", "dolce_mailer.sqlite3")

# Mail transport: "brevo" (API) or "smtp" (e.g. Google Workspace while Brevo
# activation is pending). Gmail SMTP is fine for the welcome flow and low
# volume (Workspace caps ~2,000 recipients/day and is not meant for mass
# marketing) - switch back to a transactional provider for big campaign sends.
MAIL_TRANSPORT = os.environ.get("MAIL_TRANSPORT", "brevo")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", FROM_EMAIL)
SMTP_PASS = os.environ.get("SMTP_PASS", "")

CONSENT_LABEL = "consented"
