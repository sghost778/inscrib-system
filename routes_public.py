from datetime import datetime
from flask import Blueprint, jsonify, request, session

import models

api_public = Blueprint("api_public", __name__)


# ============================
# SITE CONFIG (GET public)
# ============================
@api_public.route("/site-config", methods=["GET"])
def get_site_config():
    configs = models.SiteConfig.query.all()
    return jsonify({c.key: c.value for c in configs})


# ============================
# NOTICIAS (GET public)
# ============================
@api_public.route("/noticias", methods=["GET"])
def noticias_listar():
    activas = request.args.get("activas", "false") == "true"
    q = models.Noticia.query
    if activas:
        q = q.filter_by(activo=True)
    noticias = q.order_by(models.Noticia.fecha_publicacion.desc()).all()
    return jsonify([{
        "id": n.id, "titulo": n.titulo, "resumen": n.resumen,
        "contenido": n.contenido, "imagen": n.imagen,
        "fecha": n.fecha_publicacion.strftime("%d/%m/%Y") if n.fecha_publicacion else "",
        "activo": n.activo
    } for n in noticias])


# ============================
# PROGRAMAS (GET public)
# ============================
@api_public.route("/programas", methods=["GET"])
def programas_listar():
    programas = models.ProgramaAcademico.query.filter_by(activo=True).all()
    return jsonify([{
        "id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
        "nivel": p.nivel, "icono": p.icono
    } for p in programas])


# ============================
# GALERIA (GET public)
# ============================
@api_public.route("/galeria", methods=["GET"])
def galeria_listar():
    imagenes = models.Galeria.query.order_by(models.Galeria.fecha_subida.desc()).all()
    return jsonify([{
        "id": g.id, "titulo": g.titulo, "imagen": g.imagen,
        "descripcion": g.descripcion,
        "fecha": g.fecha_subida.strftime("%d/%m/%Y") if g.fecha_subida else ""
    } for g in imagenes])


# ============================
# CONTACTO (POST public)
# ============================
@api_public.route("/contacto", methods=["POST"])
def contacto_publico():
    data = request.get_json()
    m = models.MensajeContacto(nombre=data["nombre"], email=data["email"],
                                telefono=data.get("telefono"), mensaje=data["mensaje"])
    models.db.session.add(m)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Mensaje enviado correctamente"}), 201


# ============================
# PORTAL REPRESENTANTE
# ============================

@api_public.route("/portal/registro", methods=["POST"])
def portal_registro():
    data = request.get_json()
    if not data or not data.get('cedula') or not data.get('password'):
        return jsonify({"success": False, "message": "Cedula y contrasena requeridas"}), 400
    try:
        cedula = data['cedula'].strip()
        if models.Representante.query.filter_by(cedula=cedula).first():
            return jsonify({"success": False, "message": "Ya existe un representante con esta cedula"}), 400
        if models.Usuario.query.filter_by(usuario=cedula).first():
            return jsonify({"success": False, "message": "Este usuario ya esta registrado"}), 400

        rep = models.Representante(
            cedula=cedula,
            nombres=data.get('nombres', '').strip(),
            apellidos=data.get('apellidos', '').strip(),
            email=data.get('email', '').strip(),
            telefono=data.get('telefono', '').strip(),
            direccion_habitacion=data.get('direccion', '').strip()
        )
        models.db.session.add(rep)
        models.db.session.flush()

        from security import hash_password
        user = models.Usuario(
            nombre=rep.nombres,
            apellido=rep.apellidos,
            usuario=cedula,
            password_hash=hash_password(data['password']),
            rol='representante'
        )
        models.db.session.add(user)
        models.db.session.commit()

        return jsonify({"success": True, "message": "Registro exitoso. Ya puedes iniciar sesion."}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error al registrar: {str(e)}"}), 500


@api_public.route("/portal/login", methods=["POST"])
def portal_login():
    data = request.get_json()
    cedula = (data.get('usuario') or '').strip()
    password = data.get('password', '')
    if not cedula or not password:
        return jsonify({"success": False, "message": "Cedula y contrasena requeridas"}), 400

    user = models.Usuario.query.filter_by(usuario=cedula, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

    from security import check_password
    if not check_password(password, user.password_hash):
        return jsonify({"success": False, "message": "Contrasena incorrecta"}), 401

    rep = models.Representante.query.filter_by(cedula=cedula).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404

    session['portal_rep_cedula'] = rep.cedula
    session['portal_rep_nombre'] = f"{rep.nombres} {rep.apellidos}"
    session['portal_rep_id'] = rep.id_representante

    return jsonify({"success": True, "nombre": f"{rep.nombres} {rep.apellidos}", "cedula": rep.cedula})


@api_public.route("/portal/logout", methods=["POST"])
def portal_logout():
    session.pop('portal_rep_cedula', None)
    session.pop('portal_rep_nombre', None)
    session.pop('portal_rep_id', None)
    return jsonify({"success": True})


@api_public.route("/portal/sesion", methods=["GET"])
def portal_sesion():
    cedula = session.get('portal_rep_cedula')
    nombre = session.get('portal_rep_nombre')
    if cedula and nombre:
        return jsonify({"autenticado": True, "nombre": nombre, "cedula": cedula})
    return jsonify({"autenticado": False})


@api_public.route("/portal/grados", methods=["GET"])
def portal_grados():
    grados = models.Grado.query.all()
    return jsonify([{"id": g.id_grado, "nombre": g.nombre, "nivel": g.nivel} for g in grados])


@api_public.route("/portal/estudiantes", methods=["POST"])
def portal_crear_estudiante():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesion"}), 401
    data = request.get_json()
    cedula_escolar = data.get("cedula_escolar", "").strip()
    if not cedula_escolar:
        return jsonify({"success": False, "message": "Cedula escolar es requerida"}), 400
    if models.Estudiante.query.get(cedula_escolar):
        return jsonify({"success": False, "message": "Ya existe un estudiante con esta cedula escolar"}), 400
    ci = data.get("cedula_identidad", "").strip()
    if ci and models.Estudiante.query.filter_by(cedula_identidad=ci).first():
        return jsonify({"success": False, "message": "Ya existe un estudiante con esta cedula de identidad"}), 400
    try:
        nuevo_est = models.Estudiante(
            cedula_escolar=cedula_escolar,
            cedula_identidad=ci or None,
            nombres=data.get("nombres", ""),
            apellidos=data.get("apellidos", ""),
            fecha_nacimiento=datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d") if data.get("fecha_nacimiento") else None,
            orden_nacimiento=data.get("orden_nacimiento", 1)
        )
        models.db.session.add(nuevo_est)
        models.db.session.commit()
        return jsonify({"success": True, "message": "Estudiante registrado correctamente"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": "Error al registrar: verifica los datos ingresados"}), 400


@api_public.route("/portal/estudiantes", methods=["GET"])
def portal_mis_estudiantes():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesion"}), 401
    rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404
    inscripciones = models.Inscripcion.query.filter_by(id_representante=rep.id_representante).all()
    resultado = []
    for ins in inscripciones:
        est = ins.estudiante
        resultado.append({
            "cedula_escolar": est.cedula_escolar,
            "nombres": est.nombres,
            "apellidos": est.apellidos,
            "grado": ins.grado.nombre if ins.grado else "N/A",
            "periodo": ins.ano_escolar.periodo if ins.ano_escolar else "N/A",
            "estado": ins.estado or "REGULAR",
            "fecha": ins.fecha_inscripcion.strftime("%d/%m/%Y") if ins.fecha_inscripcion else ""
        })
    return jsonify(resultado)


@api_public.route("/portal/inscripcion", methods=["POST"])
def portal_inscribir():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesion"}), 401
    data = request.get_json()
    try:
        ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()
        if not ano_activo:
            return jsonify({"success": False, "message": "No hay ano escolar activo"}), 400
        rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
        if not rep:
            return jsonify({"success": False, "message": "Representante no encontrado"}), 404
        estudiante = models.Estudiante.query.get(data["cedula_escolar"])
        if not estudiante:
            return jsonify({"success": False, "message": "Estudiante no encontrado. Registralo primero."}), 404
        existe = models.Inscripcion.query.filter_by(
            cedula_escolar=data["cedula_escolar"], id_ano_escolar=ano_activo.id_ano
        ).first()
        if existe:
            return jsonify({"success": False, "message": "Este estudiante ya esta inscrito en el ano escolar activo"}), 400
        inscripcion = models.Inscripcion(
            cedula_escolar=data["cedula_escolar"],
            id_representante=rep.id_representante,
            id_grado=data.get("id_grado", 1),
            id_ano_escolar=ano_activo.id_ano,
            id_usuario=1,
            estado='REGULAR'
        )
        models.db.session.add(inscripcion)
        models.db.session.commit()
        return jsonify({"success": True, "message": "Inscripcion realizada exitosamente"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@api_public.route("/portal/perfil", methods=["GET", "PUT"])
def portal_perfil():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesion"}), 401
    rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404
    if request.method == "GET":
        return jsonify({"cedula": rep.cedula, "nombres": rep.nombres, "apellidos": rep.apellidos,
                        "email": rep.email or "", "telefono": rep.telefono or "", "direccion": rep.direccion_habitacion or ""})
    data = request.get_json()
    try:
        rep.nombres = data.get('nombres', rep.nombres)
        rep.apellidos = data.get('apellidos', rep.apellidos)
        rep.email = data.get('email', rep.email)
        rep.telefono = data.get('telefono', rep.telefono)
        rep.direccion_habitacion = data.get('direccion', rep.direccion_habitacion)
        user = models.Usuario.query.filter_by(usuario=cedula_rep, rol='representante').first()
        if user:
            user.nombre = rep.nombres
            user.apellido = rep.apellidos
        models.db.session.commit()
        session['portal_rep_nombre'] = f"{rep.nombres} {rep.apellidos}"
        return jsonify({"success": True, "message": "Perfil actualizado"})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@api_public.route("/portal/password", methods=["PUT"])
def portal_password():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesion"}), 401
    data = request.get_json()
    current = data.get('current', '')
    new_pass = data.get('new_password', '')
    if not current or not new_pass:
        return jsonify({"success": False, "message": "Contrasena actual y nueva requeridas"}), 400
    if len(new_pass) < 4:
        return jsonify({"success": False, "message": "La nueva contrasena debe tener al menos 4 caracteres"}), 400
    user = models.Usuario.query.filter_by(usuario=cedula_rep, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    from security import check_password, hash_password
    if not check_password(current, user.password_hash):
        return jsonify({"success": False, "message": "Contrasena actual incorrecta"}), 401
    user.password_hash = hash_password(new_pass)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Contrasena cambiada exitosamente"})


@api_public.route("/portal/recuperar", methods=["POST"])
def portal_recuperar():
    cedula = (request.get_json() or {}).get('cedula', '').strip()
    if not cedula:
        return jsonify({"success": False, "message": "Ingresa tu cedula"}), 400
    user = models.Usuario.query.filter_by(usuario=cedula, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "No se encontro una cuenta con esta cedula"}), 404
    return jsonify({"success": True, "message": "Tu cedula esta registrada. Contacta a la institucion para restablecer tu contrasena o usa la opcion de cambio desde tu perfil."})


@api_public.route("/portal/constancia/<cedula_escolar>", methods=["GET"])
def portal_constancia(cedula_escolar):
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesion"}), 401
    rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404
    inscripcion = models.Inscripcion.query.filter_by(
        cedula_escolar=cedula_escolar, id_representante=rep.id_representante
    ).first()
    if not inscripcion:
        return jsonify({"success": False, "message": "Inscripcion no encontrada"}), 404
    est = inscripcion.estudiante
    return jsonify({
        "estudiante": f"{est.nombres} {est.apellidos}",
        "cedula_escolar": est.cedula_escolar,
        "grado": inscripcion.grado.nombre if inscripcion.grado else "N/A",
        "periodo": inscripcion.ano_escolar.periodo if inscripcion.ano_escolar else "N/A",
        "estado": inscripcion.estado or "REGULAR",
        "fecha": inscripcion.fecha_inscripcion.strftime("%d/%m/%Y") if inscripcion.fecha_inscripcion else "",
        "representante": f"{rep.nombres} {rep.apellidos}",
        "rep_cedula": rep.cedula
    })
