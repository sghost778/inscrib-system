import os
from datetime import timedelta

# Ruta absoluta del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'inscribe_system_secure_key_2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'inscribe_system_secure_key_2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Seguridad de cookies (desactivada para desarrollo local)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True

    # Almacenamiento de rate limiting (memoria; suficiente para un solo proceso)
    RATELIMIT_STORAGE_URI = 'memory://'

    # --- CONEXIÓN A SQLITE PARA FLASK ---
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'test.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

