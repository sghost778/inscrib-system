"""Punto de entrada WSGI para gunicorn / hosts de la nube (Render, Railway, etc.).

Uso:  gunicorn app_combined:application
La configuración de producción (config_prod) se aplica dentro de app_combined
y requiere la variable de entorno SECRET_KEY (y opcionalmente DATABASE_URL).
"""

from app_combined import application  # noqa: F401
