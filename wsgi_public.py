# Punto de entrada de producción para el SITIO PÚBLICO
# Uso: gunicorn wsgi_public:app
from app_public import create_app

app = create_app()
