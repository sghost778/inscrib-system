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
from security import hash_password

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
    Talisman(app, content_security_policy=None, force_https=Config.FORCE_HTTPS)

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

    @app.route('/logout')
    def view_logout():
        return redirect('/login')

    @app.route('/admin/sitio')
    def view_admin_sitio():
        return render_template('admin_sitio.html')

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

    @app.route('/inicio')
    def view_inicio():
        return render_template('inicio_contenido.html')

    @app.route('/menu')
    def view_menu():
        return render_template('menu.html')

    @app.route('/usuarios')
    def view_usuarios():
        return render_template('usuarios.html')

    @app.route('/gestion-ano')
    def view_gestion_ano():
        return render_template('gestion_ano.html')

    @app.route('/estudiantes')
    def view_estudiantes_listado():
        return render_template('estudiantes_listado.html')

    @app.route('/estudiantes/registro')
    def view_estudiantes_registro():
        return render_template('estudiantes_registro.html')

    @app.route('/estudiantes/consulta')
    def view_estudiantes_consulta():
        return render_template('estudiantes_consulta.html')

    @app.route('/representantes')
    def view_representantes_listado():
        return render_template('representantes_listado.html')

    @app.route('/representantes/registro')
    def view_representantes_registro():
        return render_template('representantes_registro.html')

    @app.route('/representantes/consulta')
    def view_representantes_consulta():
        return render_template('representantes_consulta.html')

    @app.route('/matricula')
    def view_matricula():
        return render_template('matricula.html')

    @app.route('/plantillas')
    def view_plantillas_guardadas():
        return render_template('plantillas_guardadas.html')

    @app.route('/plantillas/nueva')
    def view_plantilla_nueva():
        return render_template('plantilla_nueva.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    # ---- DATABASE SETUP ----
    with app.app_context():
        db.create_all()

        try:
            db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN estado TEXT DEFAULT 'REGULAR';"))
            db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN fecha_retiro TEXT;"))
            db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN lapso_registro TEXT DEFAULT 'Lapso 1';"))
            db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN motivo_retiro TEXT;"))
            db.session.commit()
        except:
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
            db.session.execute(text("ALTER TABLE USUARIO ADD COLUMN rol TEXT DEFAULT 'admin';"))
            db.session.commit()
        except:
            db.session.rollback()

        admin = Usuario.query.filter_by(usuario='admin').first()
        if not admin:
            hashed_pw = hash_password(Config.ADMIN_PASSWORD)
            admin = Usuario(nombre='Administrador', apellido='Sistema', usuario='admin', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()
            print(f"Usuario 'admin' creado con contrasena de la variable ADMIN_PASSWORD")

        from models import Pais, Estado, Ciudad, Representante, Estudiante, Familiar, AnoEscolar, Grado, Inscripcion
        try:
            if Pais.query.count() == 0:
                p = Pais(nombre="Venezuela"); db.session.add(p); db.session.commit()
                e = Estado(nombre="Distrito Capital", id_pais=p.id_pais); db.session.add(e); db.session.commit()
                c = Ciudad(nombre="Caracas", id_estado=e.id_estado); db.session.add(c); db.session.commit()

            if Representante.query.count() == 0:
                rep1 = Representante(cedula="V-12345678", nombres="Juan Carlos", apellidos="Perez Silva", email="juan@ejemplo.com", profesion="Ingeniero", telefono="04141234567", direccion_habitacion="Caracas, El Paraiso")
                rep2 = Representante(cedula="V-87654321", nombres="Maria Fernanda", apellidos="Lopez Diaz", email="maria@ejemplo.com", profesion="Abogada", telefono="04249876543", direccion_habitacion="Caracas, Chacao")
                db.session.add_all([rep1, rep2]); db.session.commit()
                print("Datos de prueba: Representantes inyectados.")

            if AnoEscolar.query.count() == 0:
                ano = AnoEscolar(periodo="2025-2026", estado="ACTIVO"); db.session.add(ano); db.session.commit()
                for gn in ["1er Ano", "2do Ano", "3er Ano", "4to Ano", "5to Ano"]:
                    if not Grado.query.filter_by(nombre=gn).first():
                        db.session.add(Grado(nombre=gn, nivel="BACHILLERATO"))
                db.session.commit()
                print("Datos de prueba: Ano y Grados inyectados.")

            if Estudiante.query.count() == 0:
                ciudad = Ciudad.query.first()
                if ciudad:
                    est1 = Estudiante(cedula_escolar="V-11111111", cedula_identidad="V-30111222", nombres="Luis Alejandro", apellidos="Perez Gomez", orden_nacimiento=1, id_ciudad_nacimiento=ciudad.id_ciudad)
                    est2 = Estudiante(cedula_escolar="V-22222222", cedula_identidad="V-31222333", nombres="Carlos Eduardo", apellidos="Lopez Silva", orden_nacimiento=2, id_ciudad_nacimiento=ciudad.id_ciudad)
                    db.session.add_all([est1, est2]); db.session.commit()
                    print("Datos de prueba: Estudiantes inyectados.")
                    rep = Representante.query.first(); ano = AnoEscolar.query.first()
                    grado1 = Grado.query.filter_by(nombre="1er Ano").first(); grado2 = Grado.query.filter_by(nombre="2do Ano").first()
                    if rep and ano and grado1 and grado2:
                        try:
                            user_admin = Usuario.query.first(); uid = user_admin.id_usuario if user_admin else 1
                            db.session.add_all([
                                Inscripcion(cedula_escolar=est1.cedula_escolar, id_representante=rep.id_representante, id_ano_escolar=ano.id_ano, id_grado=grado1.id_grado, estado="REGULAR", id_usuario=uid),
                                Inscripcion(cedula_escolar=est2.cedula_escolar, id_representante=rep.id_representante, id_ano_escolar=ano.id_ano, id_grado=grado2.id_grado, estado="REGULAR", id_usuario=uid),
                            ]); db.session.commit()
                            print("Datos de prueba: Estudiantes inscritos (Matricula inyectada).")
                        except: db.session.rollback()
        except: db.session.rollback()

        from models import Noticia, ProgramaAcademico, Galeria, SiteConfig
        try:
            if Noticia.query.count() == 0:
                for nd in [
                    {"titulo": "Inicio de Clases 2026-2027", "resumen": "Las inscripciones para el nuevo ano escolar estan abiertas.", "contenido": "Periodo de inscripciones abierto.", "imagen": "/static/uploads/noticia1.jpg"},
                    {"titulo": "Jornada Deportiva Anual", "resumen": "Jornada deportiva con participacion de todos los niveles.", "contenido": "Jornada Deportiva Anual 2026 realizada con exito.", "imagen": "/static/uploads/noticia2.jpg"},
                    {"titulo": "Entrega de Boletines", "resumen": "Entrega de boletines del primer lapso el 15 de julio.", "contenido": "Entrega de boletines primer lapso.", "imagen": "/static/uploads/noticia3.jpg"},
                ]:
                    db.session.add(Noticia(**nd))
                db.session.commit()
                print("Datos de prueba: Noticias inyectadas.")

            if ProgramaAcademico.query.count() == 0:
                for pd in [
                    {"nombre": "Educacion Inicial", "descripcion": "Programa para ninos de 3 a 5 anos.", "nivel": "Inicial", "icono": "fa-child"},
                    {"nombre": "Educacion Primaria", "descripcion": "Formacion integral de 1ero a 6to grado.", "nivel": "Primaria", "icono": "fa-book-open"},
                    {"nombre": "Educacion Media General", "descripcion": "Bachillerato general de 1ero a 5to ano.", "nivel": "Bachillerato", "icono": "fa-graduation-cap"},
                    {"nombre": "Educacion Especial", "descripcion": "Atencion educativa integral.", "nivel": "Especial", "icono": "fa-hands-helping"},
                    {"nombre": "Formacion Docente", "descripcion": "Actualizacion y formacion continua.", "nivel": "Docente", "icono": "fa-chalkboard-teacher"},
                ]:
                    db.session.add(ProgramaAcademico(**pd))
                db.session.commit()
                print("Datos de prueba: Programas Academicos inyectados.")

            if Galeria.query.count() == 0:
                for gd in [
                    {"titulo": "Instalaciones Deportivas", "imagen": "/static/uploads/galeria1.jpg"},
                    {"titulo": "Salon de Clases", "imagen": "/static/uploads/galeria2.jpg"},
                    {"titulo": "Laboratorio de Ciencias", "imagen": "/static/uploads/galeria3.jpg"},
                    {"titulo": "Biblioteca Escolar", "imagen": "/static/uploads/galeria1.jpg"},
                    {"titulo": "Area de Recreacion", "imagen": "/static/uploads/galeria2.jpg"},
                    {"titulo": "Auditorio", "imagen": "/static/uploads/galeria3.jpg"},
                ]:
                    db.session.add(Galeria(**gd))
                db.session.commit()
                print("Datos de prueba: Galeria inyectada.")

            if SiteConfig.query.count() == 0:
                for k, v in [
                    ("site_name", "Escuela José Manuel Cova Maza"),
                    ("site_description", "Formando lideres para el futuro con excelencia educativa"),
                    ("about_title", "Quienes Somos?"),
                    ("about_content", "Institucion educativa comprometida con la formacion integral."),
                    ("about_mision", "Formar ciudadanos integrales con valores eticos."),
                    ("about_vision", "Ser institucion de referencia nacional."),
                    ("contact_address", "Av. Principal, Puerto Ordaz, Estado Bolivar"),
                    ("contact_phone", "+58 412-1234567"),
                    ("contact_email", "info@uejmcm.edu.ve"),
                    ("contact_hours", "Lunes a Viernes: 7:00 AM - 3:00 PM"),
                    ("requisitos_inscripcion", "Partida de Nacimiento\nCedula del Estudiante\nCedula del Representante\nFotos tipo carnet (2)\nCertificado de Estudios"),
                ]:
                    db.session.add(SiteConfig(key=k, value=v))
                db.session.commit()
                print("Datos de prueba: Configuracion del sitio inyectada.")

            if Usuario.query.filter_by(usuario='secretario').count() == 0:
                db.session.add(Usuario(nombre='Maria', apellido='Secretaria', usuario='secretario', password_hash=hash_password('secretario123'), rol='secretario'))
                db.session.commit()
                print("Usuario 'secretario' creado")
        except Exception as seed_err:
            db.session.rollback()
            print(f"[INFO] Seed data: {seed_err}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5001, debug=True)
