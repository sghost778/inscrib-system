from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ============================
#   1. GEOGRAFÍA
# ============================

class Pais(db.Model):
    __tablename__ = 'PAIS'
    id_pais = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Estado(db.Model):
    __tablename__ = 'ESTADO'
    id_estado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    id_pais = db.Column(db.Integer, db.ForeignKey('PAIS.id_pais'))

class Ciudad(db.Model):
    __tablename__ = 'CIUDAD'
    id_ciudad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    id_estado = db.Column(db.Integer, db.ForeignKey('ESTADO.id_estado'))

class CodigoArea(db.Model):
    __tablename__ = 'CODIGO_AREA'
    id_codigo = db.Column(db.Integer, primary_key=True)
    prefijo = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # MOVIL / FIJO

# ============================
#   2. ACADÉMICO
# ============================

class AnoEscolar(db.Model):
    __tablename__ = 'ANO_ESCOLAR'
    id_ano = db.Column(db.Integer, primary_key=True)
    periodo = db.Column(db.String(20), unique=True, nullable=False)
    estado = db.Column(db.String(10), default='ACTIVO')  # ACTIVO / CERRADO

class Grado(db.Model):
    __tablename__ = 'GRADO'
    id_grado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    nivel = db.Column(db.String(15))  # INICIAL / PRIMARIA / BACHILLERATO

class TipoRequisito(db.Model):
    __tablename__ = 'TIPO_REQUISITO'
    id_requisito = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), unique=True, nullable=False)

class Enfermedad(db.Model):
    __tablename__ = 'ENFERMEDAD'
    id_enfermedad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class Discapacidad(db.Model):
    __tablename__ = 'DISCAPACIDAD'
    id_discapacidad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(15), nullable=False)  # MOTORA / VISUAL / AUDITIVA / COGNITIVA

# ============================
#   3. USUARIOS Y SEGURIDAD
# ============================

class Usuario(db.Model):
    __tablename__ = 'USUARIO'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='admin')  # admin / secretario / docente

class RegistroAuditoria(db.Model):
    __tablename__ = 'REGISTRO_AUDITORIA'
    id_log = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('USUARIO.id_usuario'))
    accion = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.Text)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship('Usuario')

# ============================
#   4. ACTORES
# ============================

class Familiar(db.Model):
    __tablename__ = 'FAMILIAR'
    id_familiar = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True)
    nombres = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    ocupacion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    tipo_parentesco = db.Column(db.String(10))  # MADRE / PADRE

class Representante(db.Model):
    __tablename__ = 'REPRESENTANTE'
    id_representante = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    profesion = db.Column(db.String(100))
    monto_mensual_ingresos = db.Column(db.Numeric(12,2))
    direccion_habitacion = db.Column(db.Text)
    telefono = db.Column(db.String(20))

class Estudiante(db.Model):
    __tablename__ = 'ESTUDIANTE'
    cedula_escolar = db.Column(db.String(12), primary_key=True)
    cedula_identidad = db.Column(db.String(10), unique=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    orden_nacimiento = db.Column(db.Integer)
    fecha_nacimiento = db.Column(db.Date)
    id_ciudad_nacimiento = db.Column(db.Integer, db.ForeignKey('CIUDAD.id_ciudad'))
    id_madre = db.Column(db.Integer, db.ForeignKey('FAMILIAR.id_familiar'))
    id_padre = db.Column(db.Integer, db.ForeignKey('FAMILIAR.id_familiar'))

    inscripciones = db.relationship('Inscripcion', backref='estudiante', lazy=True)

# ============================
#   5. INSCRIPCIÓN
# ============================

class Inscripcion(db.Model):
    __tablename__ = 'INSCRIPCION'
    id_inscripcion = db.Column(db.Integer, primary_key=True)
    cedula_escolar = db.Column(db.String(12), db.ForeignKey('ESTUDIANTE.cedula_escolar'))
    id_representante = db.Column(db.Integer, db.ForeignKey('REPRESENTANTE.id_representante'))
    id_grado = db.Column(db.Integer, db.ForeignKey('GRADO.id_grado'))
    id_ano_escolar = db.Column(db.Integer, db.ForeignKey('ANO_ESCOLAR.id_ano'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('USUARIO.id_usuario'))
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='REGULAR')
    fecha_retiro = db.Column(db.Date)
    lapso_registro = db.Column(db.String(20), default='Lapso 1')
    motivo_retiro = db.Column(db.Text)

    grado = db.relationship('Grado')
    ano_escolar = db.relationship('AnoEscolar')
    representante = db.relationship('Representante')


# ============================
#   6. CONTENIDO PÚBLICO (WEB)
# ============================

class SiteConfig(db.Model):
    __tablename__ = 'SITE_CONFIG'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    type = db.Column(db.String(20), default='text')

class Noticia(db.Model):
    __tablename__ = 'NOTICIA'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    resumen = db.Column(db.Text)
    contenido = db.Column(db.Text)
    imagen = db.Column(db.String(500))
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

class ProgramaAcademico(db.Model):
    __tablename__ = 'PROGRAMA_ACADEMICO'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    nivel = db.Column(db.String(50))
    icono = db.Column(db.String(50), default='fa-book')
    activo = db.Column(db.Boolean, default=True)

class Galeria(db.Model):
    __tablename__ = 'GALERIA'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    imagen = db.Column(db.String(500), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

class MensajeContacto(db.Model):
    __tablename__ = 'MENSAJE_CONTACTO'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
