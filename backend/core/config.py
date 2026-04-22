"""Central config & environment."""
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "superadmin@sspl.in").lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "Fire Compliance OS <onboarding@resend.dev>")

COST_PER_ASSET = float(os.environ.get("COST_PER_ASSET", 10))
COST_PER_INSPECTION = float(os.environ.get("COST_PER_INSPECTION", 5))
COST_PER_USER = float(os.environ.get("COST_PER_USER", 20))
WALLET_LOW_THRESHOLD = float(os.environ.get("WALLET_LOW_THRESHOLD", 500))

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/app/backend/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

JWT_ALGO = "HS256"
ACCESS_MIN = 60 * 8        # 8h
REFRESH_DAYS = 7
BCRYPT_ROUNDS = 12
