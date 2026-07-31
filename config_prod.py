"""Configuración de PRODUCCIÓN para INSCRIB SYSTEM.

Uso: en los puntos de entrada de producción (app_prod.py, app_admin_prod.py,
app_combined.py) se llama a configure_production(app).

Requisitos en el hosting (ej. PythonAnywhere -> Web -> Environment variables):
    SECRET_KEY = <valor largo y aleatorio>
Opcional:
    JWT_SECRET_KEY = <valor largo y aleatorio>   (si no se da, usa SECRET_KEY)
"""

import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ProductionConfig:
    # Sin valor por defecto: en producción DEBE venir de una variable de entorno.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY or 'cambiar-en-produccion')

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Cookies seguras (la app se sirve por HTTPS en el hosting).
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    # Misma base SQLite local; en producción con más carga se recomienda
    # cambiar esto a MySQL/PostgreSQL (ej. mysql+pymysql://...).
    # Se puede sobreescribir con la variable de entorno DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'test.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Almacenamiento de rate limiting en memoria (evita el aviso de Flask-Limiter).
    RATELIMIT_STORAGE_URI = 'memory://'


def configure_production(app):
    """Aplica la configuración de producción y valida lo obligatorio."""
    app.config.from_object(ProductionConfig)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError(
            'Falta la variable de entorno SECRET_KEY. Defínela en el hosting '
            '(ej. PythonAnywhere -> Web -> Environment variables).'
        )

    app.debug = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app
