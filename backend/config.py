import os
from datetime import timedelta

class Config:
    # ── Flask & Security ───────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'crop-monitor-secret-key-2024-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # ── Session & Cookie Management ────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY    = True
    SESSION_COOKIE_SAMESITE    = 'Lax'
    REMEMBER_COOKIE_HTTPONLY   = True
    REMEMBER_COOKIE_DURATION   = timedelta(days=30)

    # ── MySQL Database ─────────────────────────────────────────────────────
    MYSQL_HOST     = os.environ.get('MYSQL_HOST',     'localhost')
    MYSQL_USER     = os.environ.get('MYSQL_USER',     'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123456')
    MYSQL_DB       = os.environ.get('MYSQL_DB',       'crop_monitoring')
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }

    # ── File Uploads ───────────────────────────────────────────────────────
    UPLOAD_FOLDER      = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024          # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

    # ── ML Model Paths ─────────────────────────────────────────────────────
    DISEASE_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'disease_detection', 'disease_model.h5')
    YIELD_MODEL_PATH   = os.path.join(os.path.dirname(__file__), '..', 'ml', 'yield_prediction',  'yield_model.pkl')
    SCALER_PATH        = os.path.join(os.path.dirname(__file__), '..', 'ml', 'yield_prediction',  'scaler.pkl')

    # ── Mail (for notifications & password reset) ──────────────────────────
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
