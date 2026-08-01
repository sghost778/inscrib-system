import os, uuid
from werkzeug.utils import secure_filename
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS

from config import Config
from models import db
from routes_public import api_public

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend_inscribe', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

def create_app():
    app = Flask(
        __name__,
        template_folder='backend_inscribe/templates',
        static_folder='backend_inscribe/static'
    )
    app.config.from_object(Config)

    db.init_app(app)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    CORS(app)

    # Register public API
    app.register_blueprint(api_public, url_prefix='/api')

    # ---- PUBLIC FRONTEND ROUTES ----

    @app.route('/manifest.json')
    def serve_manifest():
        return send_from_directory('backend_inscribe/static', 'manifest.json')

    @app.route('/sw.js')
    def serve_sw():
        return send_from_directory('backend_inscribe/static', 'sw.js', mimetype='application/javascript')

    @app.route('/')
    def view_index():
        return render_template('inicio_publico.html')

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

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se envio archivo'}), 400
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Archivo no valido'}), 400
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        url = f"/static/uploads/{filename}"
        return jsonify({'success': True, 'url': url})

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
