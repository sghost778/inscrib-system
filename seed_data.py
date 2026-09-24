# seed_data.py - Datos iniciales de prueba (una sola transaccion)
# Se ejecuta al arrancar el panel admin solo si la base de datos esta vacia.
from models import db


def seed_datos_iniciales():
    from models import (Pais, Estado, Ciudad, Representante, Estudiante, AnoEscolar, Grado,
                        Inscripcion, Noticia, ProgramaAcademico, Galeria, SiteConfig, Usuario)
    from security import hash_password

    if Pais.query.count() == 0:
        p = Pais(nombre="Venezuela")
        db.session.add(p)
        db.session.flush()
        e = Estado(nombre="Distrito Capital", id_pais=p.id_pais)
        db.session.add(e)
        db.session.flush()
        db.session.add(Ciudad(nombre="Caracas", id_estado=e.id_estado))

    if Representante.query.count() == 0:
        db.session.add_all([
            Representante(cedula="V-12345678", nombres="Juan Carlos", apellidos="Perez Silva",
                          email="juan@ejemplo.com", profesion="Ingeniero", telefono="04141234567",
                          direccion_habitacion="Caracas, El Paraiso"),
            Representante(cedula="V-87654321", nombres="Maria Fernanda", apellidos="Lopez Diaz",
                          email="maria@ejemplo.com", profesion="Abogada", telefono="04249876543",
                          direccion_habitacion="Caracas, Chacao"),
        ])

    if AnoEscolar.query.count() == 0:
        ano = AnoEscolar(periodo="2025-2026", estado="ACTIVO")
        db.session.add(ano)
        db.session.flush()
        for gn in ["1er Ano", "2do Ano", "3er Ano", "4to Ano", "5to Ano"]:
            db.session.add(Grado(nombre=gn, nivel="BACHILLERATO"))

    if Estudiante.query.count() == 0:
        ciudad = Ciudad.query.first()
        if ciudad:
            db.session.add_all([
                Estudiante(cedula_escolar="V-11111111", cedula_identidad="V-30111222",
                           nombres="Luis Alejandro", apellidos="Perez Gomez", orden_nacimiento=1,
                           id_ciudad_nacimiento=ciudad.id_ciudad),
                Estudiante(cedula_escolar="V-22222222", cedula_identidad="V-31222333",
                           nombres="Carlos Eduardo", apellidos="Lopez Silva", orden_nacimiento=2,
                           id_ciudad_nacimiento=ciudad.id_ciudad),
            ])
            db.session.flush()
            rep = Representante.query.first()
            ano = AnoEscolar.query.first()
            grado1 = Grado.query.filter_by(nombre="1er Ano").first()
            grado2 = Grado.query.filter_by(nombre="2do Ano").first()
            user_admin = Usuario.query.first()
            uid = user_admin.id_usuario if user_admin else 1
            if rep and ano and grado1 and grado2:
                db.session.add_all([
                    Inscripcion(cedula_escolar="V-11111111", id_representante=rep.id_representante,
                                id_ano_escolar=ano.id_ano, id_grado=grado1.id_grado,
                                estado="REGULAR", id_usuario=uid),
                    Inscripcion(cedula_escolar="V-22222222", id_representante=rep.id_representante,
                                id_ano_escolar=ano.id_ano, id_grado=grado2.id_grado,
                                estado="REGULAR", id_usuario=uid),
                ])

    if Noticia.query.count() == 0:
        for nd in [
            {"titulo": "Inicio de Clases 2026-2027",
             "resumen": "Las inscripciones para el nuevo año escolar estan abiertas.",
             "contenido": "Periodo de inscripciones abierto.",
             "imagen": "/static/uploads/noticia1.jpg"},
            {"titulo": "Jornada Deportiva Anual",
             "resumen": "Jornada deportiva con participacion de todos los niveles.",
             "contenido": "Jornada Deportiva Anual 2026 realizada con exito.",
             "imagen": "/static/uploads/noticia2.jpg"},
            {"titulo": "Entrega de Boletines",
             "resumen": "Entrega de boletines del primer lapso el 15 de julio.",
             "contenido": "Entrega de boletines primer lapso.",
             "imagen": "/static/uploads/noticia3.jpg"},
        ]:
            db.session.add(Noticia(**nd))

    if ProgramaAcademico.query.count() == 0:
        for pd in [
            {"nombre": "Educacion Inicial", "descripcion": "Programa para ninos de 3 a 5 anos.",
             "nivel": "Inicial", "icono": "fa-child"},
            {"nombre": "Educacion Primaria", "descripcion": "Formacion integral de 1ero a 6to grado.",
             "nivel": "Primaria", "icono": "fa-book-open"},
            {"nombre": "Educacion Media General", "descripcion": "Bachillerato general de 1ero a 5to ano.",
             "nivel": "Bachillerato", "icono": "fa-graduation-cap"},
            {"nombre": "Educacion Especial", "descripcion": "Atencion educativa integral.",
             "nivel": "Especial", "icono": "fa-hands-helping"},
            {"nombre": "Formacion Docente", "descripcion": "Actualizacion y formacion continua.",
             "nivel": "Docente", "icono": "fa-chalkboard-teacher"},
        ]:
            db.session.add(ProgramaAcademico(**pd))

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
            ("requisitos_inscripcion", "Partida de Nacimiento\nCedula del Estudiante\n"
                                        "Cedula del Representante\nFotos tipo carnet (2)\n"
                                        "Certificado de Estudios"),
        ]:
            db.session.add(SiteConfig(key=k, value=v))

    if Usuario.query.filter_by(usuario='secretario').count() == 0:
        db.session.add(Usuario(nombre='Maria', apellido='Secretaria', usuario='secretario',
                               password_hash=hash_password('secretario123'), rol='secretario'))

    db.session.commit()