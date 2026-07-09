"""Punto de entrada de PRODUCCIÓN para el PANEL DE ADMINISTRACIÓN.

Envuelve el panel administrativo de INSCRIB SYSTEM (inscripciones,
estudiantes, representantes, matrícula, usuarios, sitio) listo para un
WSGI de producción, para desplegarlo como app SEPARADA de la pública.

WSGI en PythonAnywhere:
    import sys
    path = '/home/TU_USUARIO/inscrib_system'
    if path not in sys.path:
        sys.path.insert(0, path)
    from app_admin_prod import app as application
"""

import os

from app import create_app
from config_prod import configure_production

app = configure_production(create_app())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
