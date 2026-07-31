"""Punto de entrada COMBINADO para producción (PythonAnywhere, plan de pago).

Une el sitio PÚBLICO (web institucional + portal del representante) y el
panel de ADMINISTRACIÓN en una sola aplicación Flask, para desplegarlo en
un único dominio.

El archivo WSGI en PythonAnywhere debe contener:
    import sys
    path = '/home/TU_USUARIO/inscrib_system'
    if path not in sys.path:
        sys.path.insert(0, path)
    from app_combined import app as application
"""

import os

from flask import render_template

from app import create_app
from routes_public import api_public
from config_prod import configure_production

app = configure_production(create_app())  # app de administración: DB, seed, rutas admin y /api/admin

# --- Registrar la API pública (portal del representante, sitio, contacto) ---
app.register_blueprint(api_public, url_prefix='/api')


# --- Páginas públicas (ya existen en app_public; las añadimos aquí) ---
@app.route('/nosotros')
def view_nosotros():
    return render_template('nosotros.html')


@app.route('/programas')
def view_programas():
    return render_template('programas.html')


@app.route('/noticias')
def view_noticias():
    return render_template('noticias.html')


@app.route('/galeria')
def view_galeria():
    return render_template('galeria.html')


@app.route('/contacto')
def view_contacto():
    return render_template('contacto.html')


@app.route('/noticia/<int:id>')
def view_noticia_detalle(id):
    return render_template('noticia_detalle.html', noticia_id=id)


@app.route('/requisitos')
def view_requisitos():
    return render_template('requisitos.html')


@app.route('/portal')
def view_portal():
    return render_template('portal.html')


@app.route('/registro')
def view_registro():
    return render_template('registro.html')


@app.route('/recuperar')
def view_recuperar_pub():
    return render_template('recuperar.html')


# --- La raíz '/' muestra el sitio público (el panel admin entra por /login) ---
def _public_home():
    return render_template('inicio_publico.html')


app.view_functions['view_root'] = _public_home

# Alias WSGI/gunicorn: `gunicorn app_combined:application`
application = app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
