from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

doc = Document()

title = doc.add_heading('INSCRIB SYSTEM - Sistema de Gestión Escolar', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('')
doc.add_paragraph('Documento de Resumen del Proyecto', style='Subtitle').alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Escuela: Unidad Educativa Dr. Jose Manuel Cova Maza', style='Subtitle').alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_page_break()

doc.add_heading('1. Descripción General', level=1)
doc.add_paragraph(
    'INSCRIB SYSTEM es un sistema de gestión escolar integral desarrollado en Flask (Python) '
    'con base de datos SQLite. El sistema cuenta con dos componentes principales:'
)

items = [
    ('Sitio Web Público', 'Página informativa visible para todo público sin necesidad de iniciar sesión.'),
    ('Panel Administrativo', 'Área privada con login para gestionar estudiantes, representantes, matrícula y contenido del sitio web.')
]
for bold, text in items:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(bold + ': ')
    run.bold = True
    p.add_run(text)

doc.add_heading('2. Sitio Web Público', level=1)
doc.add_paragraph('El sitio web público se accede desde la raíz (/) y contiene las siguientes secciones:')

sections = [
    ('Inicio (/)', 'Página principal con hero banner, "Por qué elegirnos", últimas noticias y formulario de contacto.'),
    ('Nosotros (/nosotros)', 'Información institucional: misión, visión, valores.'),
    ('Programas (/programas)', 'Programas académicos cargados desde BD (Inicial, Primaria, Bachillerato).'),
    ('Noticias (/noticias)', 'Noticias y eventos escolares. Cada noticia tiene página de detalle en /noticia/<id>.'),
    ('Detalle de Noticia (/noticia/<id>)', 'Página individual con contenido completo de cada noticia.'),
    ('Galería (/galeria)', 'Álbum de imágenes con vista previa y modal para ampliar.'),
    ('Contacto (/contacto)', 'Formulario de contacto público que envía mensajes a la BD.')
]
for t, desc in sections:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(t + ': ')
    run.bold = True
    p.add_run(desc)

doc.add_heading('3. Panel Administrativo (Gestión Interna)', level=1)
doc.add_paragraph(
    'Login en /login. Usuarios por defecto: admin/admin123 (admin), secretario/secretario123 (secretario). '
    'Soporta múltiples roles (admin, secretario, docente). Menú lateral con opciones:'
)

admin_sections = [
    'Inicio - Dashboard con últimos accesos',
    'Estudiantes - Listado, consulta y registro',
    'Representantes - Listado, consulta y registro',
    'Plantilla de Inscripción - Registro de matrícula',
    'Matrícula - Control de inscripciones activas',
    'Gestión de Año - Apertura/cierre de años escolares',
    'Usuarios - CRUD completo de usuarios del sistema',
    'Configurar Sitio Web - Admin completo del contenido público'
]
for s in admin_sections:
    doc.add_paragraph(s, style='List Bullet')

doc.add_heading('4. Configuración del Sitio Web', level=1)
doc.add_paragraph('Panel completo para administrar el contenido del sitio público:')

config_items = [
    ('Configuración General', 'Nombre, teléfono, email, dirección y horario de la escuela.'),
    ('Noticias', 'Crear, editar y eliminar noticias. Soporta subida de imágenes.'),
    ('Programas Académicos', 'CRUD de programas educativos con nombre, descripción, nivel e icono.'),
    ('Galería', 'Agregar y eliminar imágenes con subida de archivos.'),
    ('Mensajes', 'Visualizar mensajes del formulario de contacto.')
]
for t, desc in config_items:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(t + ': ')
    run.bold = True
    p.add_run(desc)

doc.add_heading('5. Roles de Usuario', level=1)
doc.add_paragraph('El sistema soporta 3 roles de usuario:')
roles = [
    ('admin', 'Acceso completo a todas las funciones del sistema.'),
    ('secretario', 'Gestión de estudiantes, representantes e inscripciones.'),
    ('docente', 'Acceso limitado a consulta de estudiantes y matrícula.')
]
for r, desc in roles:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(r + ': ')
    run.bold = True
    p.add_run(desc)

doc.add_heading('6. Sistema de Subida de Archivos', level=1)
doc.add_paragraph(
    'Endpoint /api/upload permite subir imágenes al servidor. Las imágenes se guardan '
    'en /static/uploads/ con nombres únicos UUID. Formatos permitidos: png, jpg, jpeg, gif, webp, svg.'
)

doc.add_heading('7. Tecnologías Utilizadas', level=1)
techs = [
    'Backend: Python 3 + Flask',
    'Base de Datos: SQLite con SQLAlchemy ORM',
    'Frontend: HTML5, CSS3, JavaScript (vanilla)',
    'Estilos: Font Awesome 6, diseño responsivo',
    'Seguridad: bcrypt, flask-limiter, flask-talisman',
    'Subida de Archivos: Werkzeug secure_filename + UUID'
]
for t in techs:
    doc.add_paragraph(t, style='List Bullet')

doc.add_heading('8. Estructura de la Base de Datos', level=1)
doc.add_paragraph('El sistema cuenta con 20 tablas:')

tables = [
    'USUARIO - Usuarios con soporte de roles (admin/secretario/docente)',
    'ESTUDIANTE - Datos de los estudiantes',
    'REPRESENTANTE - Datos de los representantes',
    'INSCRIPCION - Registro de matrícula',
    'GRADO - Grados académicos',
    'ANO_ESCOLAR - Años escolares',
    'FAMILIAR - Datos de padres/madres',
    'PAIS, ESTADO, CIUDAD - Datos geográficos',
    'REGISTRO_AUDITORIA - Registro de actividades',
    'SITE_CONFIG - Configuración del sitio web',
    'NOTICIA - Noticias y eventos',
    'PROGRAMA_ACADEMICO - Programas educativos',
    'GALERIA - Imágenes de la galería',
    'MENSAJE_CONTACTO - Mensajes de contacto'
]
for t in tables:
    doc.add_paragraph(t, style='List Bullet')

doc.add_heading('9. Mejoras y Correcciones Aplicadas', level=1)
fixes = [
    'Corregido bug: Grado.capacidad no existía en el modelo',
    'Corregido bug: Grado.nivel tenía NOT NULL sin valor por defecto',
    'Agregado: Página de detalle de noticia (/noticia/<id>)',
    'Agregado: Sistema de subida de imágenes con /api/upload',
    'Agregado: Roles de usuario (admin, secretario, docente)',
    'Agregado: CRUD completo de usuarios via API',
    'Agregado: Sidebar responsive (colapsable en móvil)',
    'Agregado: Datos de semilla para noticias, programas y galería',
    'Agregado: Usuario secundario "secretario" para pruebas',
    'Agregado: requirements.txt con dependencias del proyecto',
    'Corregido: UnicodeEncodeError en prints con emojis',
    'Actualizado: Login devuelve rol del usuario',
    'Actualizado: Todos los enlaces internos (/, /login, etc.)'
]
for f in fixes:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('10. Cómo Ejecutar el Sistema', level=1)
steps = [
    'Abrir terminal en la carpeta del proyecto',
    'pip install -r requirements.txt (solo la primera vez)',
    'python create_db_table.py (crea la BD con datos de prueba)',
    'python app.py',
    'Abrir navegador en http://localhost:5000 (sitio público)',
    'Ir a http://localhost:5000/login (panel admin)',
    'Usuarios: admin/admin123 o secretario/secretario123'
]
for s in steps:
    doc.add_paragraph(s, style='List Number')

doc.add_paragraph('')
doc.add_paragraph('--- Fin del Documento ---').alignment = WD_ALIGN_PARAGRAPH.CENTER

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RESUMEN_PROYECTO_INSCRIB.docx')
doc.save(output_path)
print(f'Documento creado: {output_path}')
