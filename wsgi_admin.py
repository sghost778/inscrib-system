# Punto de entrada de producción para el PANEL ADMIN
# Uso: gunicorn wsgi_admin:app
from app import create_app

app = create_app()
