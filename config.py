import os
from datetime import timedelta

# Ruta absoluta del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'inscribe_system_secure_key_2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'inscribe_system_secure_key_2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true'

    # Seguridad de cookies: True en producción (https), False en desarrollo local
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', str(not DEBUG)).lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # --- BASE DE DATOS ---
    # En producción (Render) se usa DATABASE_URL (PostgreSQL).
    # En desarrollo local se usa SQLite (test.db).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'test.db')}"
    )
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql+psycopg://', 1)
    elif SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgresql://', 'postgresql+psycopg://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Contraseña inicial para el usuario 'admin' (solo se usa si no existe)
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
