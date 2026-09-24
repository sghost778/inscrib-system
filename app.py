import os, uuid
from werkzeug.utils import secure_filename
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from models import db, Usuario
from sqlalchemy import text
from routes_admin import api_admin
from security import hash_password, login_requerido, token_required
from db_migrate import migrar_bd

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
    limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
    Talisman(app, content_security_policy=None, force_https=Config.FORCE_HTTPS,
             session_cookie_secure=Config.SESSION_COOKIE_SECURE)

    app.register_blueprint(api_admin, url_prefix='/api')

    # ---- ADMIN FRONTEND ROUTES ----

    @app.route('/manifest.json')
    def serve_manifest():
        return send_from_directory('backend_inscribe/static', 'manifest.json')

    @app.route('/sw.js')
    def serve_sw():
        return send_from_directory('backend_inscribe/static', 'sw.js', mimetype='application/javascript')

    @app.route('/')
    def view_root():
        return redirect('/login')

    @app.route('/login')
    def view_login():
        return render_template('login.html')

    @app.route('/registro')
    @login_requerido
    def view_registro():
        return render_template('registro.html')

    @app.route('/recuperar')
    def view_recuperar():
        return render_template('recuperar.html')

    @app.route('/restablecer')
    def view_restablecer():
        return render_template('restablecer.html')

    @app.route('/logout')
    def view_logout():
        return redirect('/login')

    @app.route('/admin/sitio')
    @login_requerido
    def view_admin_sitio():
        return render_template('admin_sitio.html')

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/api/upload', methods=['POST'])
    @token_required
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se envio archivo'}), 400
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Archivo no valido'}), 400
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        raw = file.read()
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as fh:
                fh.write(raw)
        except Exception as save_err:
            print(f"[UPLOAD] disco no disponible: {save_err}")
        import base64 as _b64
        mime = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'gif': 'gif',
                'webp': 'webp', 'svg': 'svg+xml'}.get(ext, ext)
        data_uri = f"data:image/{mime};base64," + _b64.b64encode(raw).decode('ascii')
        return jsonify({'success': True, 'url': data_uri,
                        'path': f"/static/uploads/{filename}"})

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    @app.route('/inicio')
    @login_requerido
    def view_inicio():
        return render_template('inicio_contenido.html')

    @app.route('/menu')
    @login_requerido
    def view_menu():
        return render_template('menu.html')

    @app.route('/reportes')
    @login_requerido
    def view_reportes():
        return render_template('reportes.html')

    @app.route('/usuarios')
    @login_requerido
    def view_usuarios():
        return render_template('usuarios.html')

    @app.route('/gestion-ano')
    @login_requerido
    def view_gestion_ano():
        return render_template('gestion_ano.html')

    @app.route('/estudiantes')
    @login_requerido
    def view_estudiantes_listado():
        return render_template('estudiantes_listado.html')

    @app.route('/estudiantes/registro')
    @login_requerido
    def view_estudiantes_registro():
        return render_template('estudiantes_registro.html')

    @app.route('/estudiantes/consulta')
    @login_requerido
    def view_estudiantes_consulta():
        from flask import redirect, url_for
        return redirect(url_for('view_estudiantes_listado'))

    @app.route('/representantes')
    @login_requerido
    def view_representantes_listado():
        return render_template('representantes_listado.html')

    @app.route('/representantes/registro')
    @login_requerido
    def view_representantes_registro():
        return render_template('representantes_registro.html')

    @app.route('/representantes/consulta')
    @login_requerido
    def view_representantes_consulta():
        from flask import redirect, url_for
        return redirect(url_for('view_representantes_listado'))

    @app.route('/matricula')
    @login_requerido
    def view_matricula():
        return render_template('matricula.html')

    @app.route('/plantillas')
    @login_requerido
    def view_plantillas_guardadas():
        return render_template('plantillas_guardadas.html')

    @app.route('/plantillas/nueva')
    @login_requerido
    def view_plantilla_nueva():
        return render_template('plantilla_nueva.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    # ---- DATABASE SETUP ----
    with app.app_context():
        try:
            migrar_bd()
        except Exception as e:
            db.session.rollback()
            print(f"[INFO] migrar_bd no critico: {e}")

        # Migraciones legacy (SQLite). Sin efecto en bases nuevas o Postgres.
        for ddl in (
            "ALTER TABLE INSCRIPCION ADD COLUMN estado TEXT DEFAULT 'REGULAR';",
            "ALTER TABLE INSCRIPCION ADD COLUMN fecha_retiro TEXT;",
            "ALTER TABLE INSCRIPCION ADD COLUMN lapso_registro TEXT DEFAULT 'Lapso 1';",
            "ALTER TABLE INSCRIPCION ADD COLUMN motivo_retiro TEXT;",
            "ALTER TABLE USUARIO ADD COLUMN rol TEXT DEFAULT 'admin';",
        ):
            try:
                db.session.execute(text(ddl))
                db.session.commit()
            except Exception:
                db.session.rollback()

        try:
            col_type = db.session.execute(
                text("SELECT type FROM pragma_table_info('REGISTRO_AUDITORIA') WHERE name='id_log'")
            ).scalar()
            if col_type and col_type.upper() != "INTEGER":
                db.session.execute(text(
                    "CREATE TABLE IF NOT EXISTS REGISTRO_AUDITORIA_new ("
                    "  id_log     INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "  id_usuario INTEGER,"
                    "  accion     TEXT NOT NULL,"
                    "  detalle    TEXT,"
                    "  fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,"
                    "  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)"
                    ")"
                ))
                db.session.execute(text(
                    "INSERT INTO REGISTRO_AUDITORIA_new (id_usuario, accion, detalle, fecha_hora) "
                    "SELECT id_usuario, accion, detalle, fecha_hora FROM REGISTRO_AUDITORIA"
                ))
                db.session.execute(text("DROP TABLE REGISTRO_AUDITORIA"))
                db.session.execute(text("ALTER TABLE REGISTRO_AUDITORIA_new RENAME TO REGISTRO_AUDITORIA"))
                db.session.commit()
                print("[OK] Migracion: REGISTRO_AUDITORIA.id_log corregida a INTEGER AUTOINCREMENT")
        except Exception as mig_err:
            db.session.rollback()
            print(f"[INFO] Migracion de auditoria omitida: {mig_err}")

        try:
            admin = Usuario.query.filter_by(usuario='admin').first()
            if not admin:
                admin = Usuario(nombre='Administrador', apellido='Sistema', usuario='admin',
                                password_hash=hash_password(Config.ADMIN_PASSWORD))
                db.session.add(admin)
                db.session.commit()
                print(f"Usuario 'admin' creado con contrasena de la variable ADMIN_PASSWORD")
        except Exception as admin_err:
            db.session.rollback()
            print(f"[INFO] Creacion del usuario admin omitida: {admin_err}")

        try:
            from seed_data import seed_datos_iniciales
            seed_datos_iniciales()
        except Exception as seed_err:
            db.session.rollback()
            print(f"[INFO] Seed data: {seed_err}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5001, debug=True)
