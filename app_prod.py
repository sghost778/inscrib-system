"""Punto de entrada para producción (PythonAnywhere / hosting).

Envuelve el sitio PÚBLICO de INSCRIB SYSTEM (sitio web institucional +
portal del representante) listo para ser servido por un WSGI de producción.

Para usarlo en PythonAnywhere, el archivo WSGI debe contener:
    import sys
    path = '/home/TU_USUARIO/mysite'
    if path not in sys.path:
        sys.path.insert(0, path)
    from app_prod import app as application
"""

import os

from app_public import create_app
from config_prod import configure_production

app = configure_production(create_app())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
