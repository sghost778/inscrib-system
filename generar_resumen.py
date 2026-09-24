from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

doc = Document()

title = doc.add_heading('INSCRIB SYSTEM - Sistema de Gestion Escolar', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('')
doc.add_paragraph('Resumen Integral del Proyecto', style='Subtitle').alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Escuela Jose Manuel Cova Maza', style='Subtitle').alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Plataforma web: https://inscrib-admin.onrender.com', style='Subtitle').alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_page_break()

# 1
doc.add_heading('1. Descripcion General', level=1)
doc.add_paragraph(
    'INSCRIB SYSTEM es una plataforma web integral de gestion escolar desarrollada en Python (Flask), '
    'con base de datos PostgreSQL en produccion (Render) y SQLite en desarrollo local. '
    'El sistema esta compuesto por tres componentes principales:'
)
items = [
    ('Sitio Web Publico', 'Pagina institucional accesible sin sesion: informacion, noticias, programas academicos, galeria, requisitos y contacto.'),
    ('Portal de Representantes', 'Area privada donde los representantes se autentican con su cedula, consultan a sus estudiantes e inscriben en linea.'),
    ('Panel Administrativo', 'Area privada con login, roles y auditoria para gestionar estudiantes, representantes, matricula, contenido del sitio, correos y reportes.'),
]
for bold, text in items:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(bold + ': ')
    run.bold = True
    p.add_run(text)

doc.add_heading('Metricas del Proyecto', level=2)
metrics = [
    '40 paginas web (26 administrativas + 14 publicas)',
    '61 endpoints API (43 admin + 18 publicos)',
    '21 tablas en la base de datos',
    'Mas de 12.000 lineas de codigo (Python + HTML/JavaScript)',
    '5 commits con historial de versiones en GitHub',
    'Despliegue automatico en Render (servicios + base de datos)',
]
for m in metrics:
    doc.add_paragraph(m, style='List Bullet')

# 2
doc.add_heading('2. Sitio Web Publico', level=1)
sections = [
    ('Inicio (/)', 'Banner principal, razones para elegir la escuela, ultimas noticias y formulario de contacto.'),
    ('Nosotros (/nosotros)', 'Mision, vision y valores institucionales.'),
    ('Programas (/programas)', 'Programas academicos cargados desde la base de datos (Inicial, Primaria, Bachillerato).'),
    ('Noticias (/noticias)', 'Noticias y eventos escolares con pagina de detalle individual.'),
    ('Galeria (/galeria)', 'Album de imagenes con vista ampliada en modal.'),
    ('Requisitos (/requisitos)', 'Lista de requisitos de inscripcion.'),
    ('Contacto (/contacto)', 'Formulario publico que almacena mensajes en la BD para el panel.'),
    ('Portal (/portal)', 'Acceso de representantes: login, registro, recuperacion de clave e inscripcion en linea.'),
]
for t, desc in sections:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(t + ': ')
    run.bold = True
    p.add_run(desc)

# 3
doc.add_heading('3. Portal del Representante', level=1)
portal = [
    'Registro con cedula, correo y clave (cuenta con rol representante).',
    'Inicio de sesion con cedula y clave.',
    'Consulta de estudiantes vinculados y su estado de inscripcion.',
    'Inscripcion en linea: seleccion de grado y ano escolar activo.',
    'Actualizacion de perfil y cambio de clave.',
    'Recuperacion de clave por enlace enviado a su correo electronico.',
    'Correos automaticos: bienvenida, confirmacion de inscripcion y aviso de cambio de clave.',
]
for s in portal:
    doc.add_paragraph(s, style='List Bullet')

# 4
doc.add_heading('4. Panel Administrativo', level=1)
doc.add_paragraph(
    'Acceso en /login. Incluye menu lateral, autenticacion por sesion y registro de auditoria de acciones.'
)
admin_sections = [
    ('Dashboard (/inicio)', 'Tarjetas KPI (estudiantes, representantes, matricula, usuarios, mensajes, retiros) y 3 graficas interactivas con Chart.js: matricula por grado, inscripciones por mes y usuarios por rol. Ultimos accesos al sistema en tiempo real.'),
    ('Estudiantes', 'Listado con busqueda, consulta detallada y registro con datos personales, nacimiento, salud y ubicacion.'),
    ('Representantes', 'Listado, consulta y registro con vinculo a estudiantes.'),
    ('Plantilla de Inscripcion', 'Formulario de matricula con datos del estudiante y representantes.'),
    ('Matricula', 'Control de inscripciones activas por grado, lapso y estado (regular/retirado).'),
    ('Gestion de Ano Escolar', 'Apertura y cierre de anos escolares con periodo y cupo.'),
    ('Usuarios', 'CRUD de usuarios con selector de rol (5 roles) y columna de rol en la tabla.'),
    ('Configurar Sitio Web', 'Edicion de noticias, programas, galeria, datos de la escuela y mensajes de contacto.'),
    ('Enviar Correo', 'Envio de correos HTML a representantes desde el panel (con plantilla institucional).'),
    ('Reportes PDF (/reportes)', 'Generacion y descarga de 5 reportes en PDF: estudiantes, matricula, representantes, usuarios y resumen estadistico.'),
]
for t, desc in admin_sections:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(t + ': ')
    run.bold = True
    p.add_run(desc)

# 5
doc.add_heading('5. Roles de Usuario', level=1)
roles = [
    ('admin', 'Acceso total a todas las funciones del sistema.'),
    ('director', 'Vision general del panel y reportes.'),
    ('secretario', 'Gestion de estudiantes, representantes e inscripciones.'),
    ('coordinador', 'Coordinacion academica y consulta de matricula.'),
    ('docente', 'Acceso limitado a consulta de estudiantes y matricula.'),
    ('representante', 'Solo portal publico: sus estudiantes e inscripciones (no entra al panel).'),
]
for r, desc in roles:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(r + ': ')
    run.bold = True
    p.add_run(desc)

# 6
doc.add_heading('6. Sistema de Correos Electronicos', level=1)
doc.add_paragraph(
    'El sistema envia correos automaticos via SMTP configurable por variables de entorno '
    '(SMTP_HOST, SMTP_USER, SMTP_PASSWORD). Correos disponibles:'
)
emails = [
    'Bienvenida al crear cuenta en el portal.',
    'Confirmacion de inscripcion del estudiante.',
    'Aviso de cambio de contrasena.',
    'Recuperacion de contrasena con enlace seguro (token valido por 1 hora).',
    'Envio manual de correos desde el panel administrativo.',
]
for e in emails:
    doc.add_paragraph(e, style='List Bullet')

# 7
doc.add_heading('7. Seguridad', level=1)
security = [
    'Contrasenas cifradas con bcrypt (no se almacenan en texto plano).',
    'Sesiones HTTP protegidas con cookies Secure en produccion (HTTPS).',
    'Flask-Talisman: cabeceras de seguridad y forzado de HTTPS.',
    'Flask-Limiter: limite de intentos de login para evitar fuerza bruta.',
    'Tokens de recuperacion de clave con expiracion de 1 hora.',
    'Registro de auditoria (REGISTRO_AUDITORIA): quien hizo que y cuando.',
    'Validacion de roles en endpoints protegidos.',
    'Subida de archivos restringida a imagenes, con nombres UUID unicos.',
]
for s in security:
    doc.add_paragraph(s, style='List Bullet')

# 8
doc.add_heading('8. Tecnologias Utilizadas', level=1)
techs = [
    'Backend: Python 3 + Flask 3.1',
    'Base de datos: PostgreSQL (produccion en Render) / SQLite (desarrollo) con SQLAlchemy ORM',
    'Frontend: HTML5, CSS3, JavaScript vanilla',
    'Graficas: Chart.js 4',
    'Reportes PDF: FPDF2',
    'Correos: smtplib (SMTP/STARTTLS)',
    'Seguridad: bcrypt, Flask-Talisman, Flask-Limiter',
    'PWA: manifest.json + Service Worker (funciona como app instalable)',
    'Servidor de produccion: Gunicorn',
    'Despliegue: Render (Blueprint con 2 servicios web + 1 base de datos)',
    'Control de versiones: Git + GitHub',
    'Iconos: Font Awesome 6',
]
for t in techs:
    doc.add_paragraph(t, style='List Bullet')

# 9
doc.add_heading('9. Base de Datos (21 tablas)', level=1)
tables = [
    'USUARIO - Usuarios del panel con 5 roles + representantes',
    'RESET_TOKEN - Tokens de recuperacion de clave',
    'REGISTRO_AUDITORIA - Log de actividades',
    'ESTUDIANTE - Datos personales y academicos',
    'REPRESENTANTE - Datos de tutores legales',
    'FAMILIAR - Informacion familiar complementaria',
    'INSCRIPCION - Matricula por grado, ano y estado',
    'ANO_ESCOLAR - Anos escolares con periodo y estado',
    'GRADO - Grados academicos por nivel',
    'PAIS / ESTADO / CIUDAD / CODIGO_AREA - Datos geograficos',
    'TIPO_REQUISITO - Requisitos de inscripcion',
    'ENFERMEDAD / DISCAPACIDAD - Salud del estudiante',
    'SITE_CONFIG - Configuracion del sitio (pares clave-valor)',
    'NOTICIA - Noticias y eventos',
    'PROGRAMA_ACADEMICO - Programas educativos',
    'GALERIA - Imagenes de la galeria',
    'MENSAJE_CONTACTO - Mensajes del formulario publico',
]
for t in tables:
    doc.add_paragraph(t, style='List Bullet')

# 10
doc.add_heading('10. Despliegue en Produccion', level=1)
deploy = [
    'Servicio inscrib-admin: panel administrativo (https://inscrib-admin.onrender.com).',
    'Servicio inscrib-publico: sitio publico y portal de representantes.',
    'Base de datos inscrib-db: PostgreSQL gestionado por Render.',
    'Blueprint render.yaml: crea los 3 recursos con un solo clic.',
    'Variables de entorno: SECRET_KEY, DATABASE_URL, FORCE_HTTPS, SMTP_*, ADMIN_PASSWORD.',
    'Arranque blindado: migraciones, seed de datos y creacion de admin se ejecutan con manejo de errores (la app no se cae si un paso falla).',
]
for d in deploy:
    doc.add_paragraph(d, style='List Bullet')

# 11
doc.add_heading('11. Mejoras y Correcciones Destacadas', level=1)
fixes = [
    'Dashboard rediseñado con graficas Chart.js y datos en tiempo real (reemplazo de tabla estatica).',
    '5 reportes PDF descargables desde el panel.',
    'Ampliacion de roles de 3 a 5 (admin, director, secretario, coordinador, docente).',
    'Portal de representantes con inscripcion en linea y recuperacion de clave por correo.',
    'Correos automaticos (bienvenida, inscripcion, cambio y recuperacion de clave).',
    'Fix critico: cookie Secure rompia el login en local (Flask-Talisman).',
    'Fix critico: base de datos Postgres expirada en Render (migracion a nueva instancia).',
    'Fix: migraciones SQL con manejo de errores por dialecto (SQLite vs PostgreSQL).',
    'Seed de datos en una sola transaccion (atomico, no deja datos a medias).',
    'Service Worker corregido: estrategia red-primero para paginas (sin caché obsoleta).',
    'PWA instalable: el panel se puede instalar como aplicacion en el escritorio.',
    'Limitador de intentos de login y cabeceras de seguridad HTTP.',
]
for f in fixes:
    doc.add_paragraph(f, style='List Bullet')

# 12
doc.add_heading('12. Como Ejecutar el Sistema (Desarrollo Local)', level=1)
steps = [
    'Abrir terminal en la carpeta del proyecto.',
    'pip install -r requirements.txt (solo la primera vez).',
    'python app.py  (arranca el panel admin en http://localhost:5001).',
    'python app_public.py  (arranca el sitio publico en http://localhost:5000).',
    'Login admin: usuario admin / clave admin123.',
    'Login secundario: usuario secretario / clave secretario123.',
    'La base de datos local (test.db) se crea y se siembra automaticamente al arrancar.',
]
for s in steps:
    doc.add_paragraph(s, style='List Number')

doc.add_paragraph('')
pfin = doc.add_paragraph('--- Fin del Documento ---')
pfin.alignment = WD_ALIGN_PARAGRAPH.CENTER

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RESUMEN_PROYECTO_INSCRIB.docx')
doc.save(output_path)
print(f'Documento creado: {output_path}')
