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

CONSENT_LABEL = "consented"
