from datetime import datetime
from flask import Blueprint, jsonify, request, session

import models
from security import check_password, log_audit, token_required

api_admin = Blueprint("api_admin", __name__)


# ============================
# HELPER
# ============================
def _hacer_sesion_y_responder(user):
    uid = user.id_usuario
    uname = user.usuario
    nombre = " ".join(filter(None, [user.nombre or "", user.apellido or ""])).strip() or uname
    rol = getattr(user, 'rol', 'admin')
    session.clear()
    session["user_id"] = uid
    session["usuario"] = uname
    session["rol"] = rol
    session.permanent = True
    log_audit(uid, "LOGIN", "Inicio de sesion exitoso")
    return jsonify({"success": True, "usuario": nombre, "rol": rol})


# ============================
# LOGIN / LOGOUT
# ============================
@api_admin.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    if not data and request.form:
        data = {"usuario": request.form.get("usuario"), "password": request.form.get("password")}
    usuario = (data.get("usuario") or "admin").strip()
    password = data.get("password", "")
    if not password:
        return jsonify({"success": False, "message": "Contrasena requerida"}), 400
    try:
        models.db.session.rollback()
        user = models.Usuario.query.filter_by(usuario=usuario).first()
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 401
        if not check_password(password, user.password_hash):
            return jsonify({"success": False, "message": "Contrasena incorrecta"}), 401
        return _hacer_sesion_y_responder(user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error en servidor: {str(e)}"}), 500


@api_admin.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ============================
# LOGS
# ============================
@api_admin.route("/dashboard/logs", methods=["GET"])
@token_required
def get_logs():
    logs = models.RegistroAuditoria.query.order_by(models.RegistroAuditoria.fecha_hora.desc()).limit(10).all()
    resultado = []
    for log in logs:
        resultado.append({
            "usuario": log.usuario.usuario,
            "nombre": f"{log.usuario.nombre} {log.usuario.apellido}",
            "fecha": log.fecha_hora.strftime("%d/%m/%Y"),
            "hora": log.fecha_hora.strftime("%I:%M %p"),
            "accion": log.accion,
        })
    return jsonify(resultado)


# ============================
# USUARIOS CRUD
# ============================
@api_admin.route("/usuarios", methods=["GET"])
@token_required
def listar_usuarios():
    usuarios = models.Usuario.query.all()
    return jsonify({"success": True, "usuarios": [{
        "id_usuario": u.id_usuario,
        "nombre_completo": f"{u.nombre or ''} {u.apellido or ''}".strip() or u.usuario,
        "usuario": u.usuario, "rol": getattr(u, 'rol', 'admin'), "estado": "activo"
    } for u in usuarios]})


@api_admin.route("/usuarios", methods=["POST"])
@token_required
def crear_usuario():
    data = request.get_json()
    exists = models.Usuario.query.filter_by(usuario=data["usuario"]).first()
    if exists:
        return jsonify({"success": False, "message": "El usuario ya existe"}), 400
    from security import hash_password
    u = models.Usuario(nombre=data.get("nombre", ""), apellido=data.get("apellido", ""),
                       usuario=data["usuario"], password_hash=hash_password(data["password"]),
                       rol=data.get("rol", "secretario"))
    models.db.session.add(u)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Usuario creado correctamente"}), 201


@api_admin.route("/usuarios/<int:id>", methods=["PUT"])
@token_required
def actualizar_usuario(id):
    u = models.Usuario.query.get_or_404(id)
    data = request.get_json()
    if "nombre" in data: u.nombre = data["nombre"]
    if "apellido" in data: u.apellido = data["apellido"]
    if "password" in data and data["password"]:
        from security import hash_password
        u.password_hash = hash_password(data["password"])
    if "rol" in data: u.rol = data["rol"]
    models.db.session.commit()
    return jsonify({"success": True, "message": "Usuario actualizado"})


@api_admin.route("/usuarios/<int:id>", methods=["DELETE"])
@token_required
def eliminar_usuario(id):
    u = models.Usuario.query.get_or_404(id)
    if u.usuario == 'admin':
        return jsonify({"success": False, "message": "No se puede eliminar el usuario admin"}), 400
    models.db.session.delete(u)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Usuario eliminado"})


# ============================
# SITE CONFIG (PUT admin)
# ============================
@api_admin.route("/site-config", methods=["PUT"])
@token_required
def put_site_config():
    data = request.get_json()
    for key, value in data.items():
        c = models.SiteConfig.query.filter_by(key=key).first()
        if c:
            c.value = str(value)
        else:
            models.db.session.add(models.SiteConfig(key=key, value=str(value)))
    models.db.session.commit()
    return jsonify({"success": True})


# ============================
# NOTICIAS (POST/PUT/DELETE admin)
# ============================
@api_admin.route("/noticias", methods=["POST"])
@token_required
def noticias_crear():
    data = request.get_json()
    n = models.Noticia(titulo=data["titulo"], resumen=data.get("resumen"),
                       contenido=data.get("contenido"), imagen=data.get("imagen"))
    models.db.session.add(n)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Noticia creada"}), 201


@api_admin.route("/noticias/<int:id>", methods=["PUT", "DELETE"])
@token_required
def noticia_id(id):
    n = models.Noticia.query.get_or_404(id)
    if request.method == "DELETE":
        models.db.session.delete(n)
        models.db.session.commit()
        return jsonify({"success": True, "message": "Noticia eliminada"})
    data = request.get_json()
    for campo in ("titulo", "resumen", "contenido", "imagen", "activo"):
        if campo in data:
            setattr(n, campo, data[campo])
    models.db.session.commit()
    return jsonify({"success": True, "message": "Noticia actualizada"})


# ============================
# PROGRAMAS (POST/PUT/DELETE admin)
# ============================
@api_admin.route("/programas", methods=["POST"])
@token_required
def programas_crear():
    data = request.get_json()
    p = models.ProgramaAcademico(nombre=data["nombre"], descripcion=data.get("descripcion"),
                                  nivel=data.get("nivel"), icono=data.get("icono", "fa-book"))
    models.db.session.add(p)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Programa creado"}), 201


@api_admin.route("/programas/<int:id>", methods=["PUT", "DELETE"])
@token_required
def programa_id(id):
    p = models.ProgramaAcademico.query.get_or_404(id)
    if request.method == "DELETE":
        models.db.session.delete(p)
        models.db.session.commit()
        return jsonify({"success": True, "message": "Programa eliminado"})
    data = request.get_json()
    for campo in ("nombre", "descripcion", "nivel", "icono", "activo"):
        if campo in data:
            setattr(p, campo, data[campo])
    models.db.session.commit()
    return jsonify({"success": True, "message": "Programa actualizado"})


# ============================
# GALERIA (POST/DELETE admin)
# ============================
@api_admin.route("/galeria", methods=["POST"])
@token_required
def galeria_crear():
    data = request.get_json()
    g = models.Galeria(titulo=data.get("titulo"), imagen=data["imagen"],
                        descripcion=data.get("descripcion"))
    models.db.session.add(g)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Imagen agregada"}), 201


@api_admin.route("/galeria/<int:id>", methods=["DELETE"])
@token_required
def galeria_id(id):
    g = models.Galeria.query.get_or_404(id)
    models.db.session.delete(g)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Imagen eliminada"})


# ============================
# MENSAJES
# ============================
@api_admin.route("/mensajes", methods=["GET"])
@token_required
def mensajes():
    msgs = models.MensajeContacto.query.order_by(models.MensajeContacto.fecha.desc()).all()
    return jsonify([{
        "id": m.id, "nombre": m.nombre, "email": m.email,
        "telefono": m.telefono, "mensaje": m.mensaje,
        "fecha": m.fecha.strftime("%d/%m/%Y %I:%M %p") if m.fecha else "",
        "leido": m.leido
    } for m in msgs])


@api_admin.route("/mensajes/<int:id>/leer", methods=["PUT"])
@token_required
def mensaje_leer(id):
    m = models.MensajeContacto.query.get_or_404(id)
    m.leido = True
    models.db.session.commit()
    return jsonify({"success": True})


# ============================
# ESTUDIANTES CRUD
# ============================
@api_admin.route("/estudiantes", methods=["POST"])
@token_required
def crear_estudiante():
    data = request.get_json()
    try:
        nuevo_est = models.Estudiante(
            cedula_escolar=data["cedula_escolar"],
            cedula_identidad=data.get("cedula_identidad"),
            nombres=data["nombres"], apellidos=data["apellidos"],
            fecha_nacimiento=datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d"),
            orden_nacimiento=data.get("orden_nacimiento"))
        models.db.session.add(nuevo_est)
        models.db.session.commit()
        log_audit(request.user.id_usuario, "REGISTRO_ESTUDIANTE", f"Cedula: {nuevo_est.cedula_escolar}")
        return jsonify({"message": "Estudiante registrado correctamente"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al registrar estudiante: {str(e)}"}), 500


@api_admin.route("/estudiantes/<cedula>", methods=["PUT"])
@token_required
def actualizar_estudiante(cedula):
    data = request.get_json()
    try:
        est = models.Estudiante.query.get(cedula)
        if not est:
            return jsonify({"message": "Estudiante no encontrado"}), 404
        if "nombres" in data: est.nombres = data["nombres"]
        if "apellidos" in data: est.apellidos = data["apellidos"]
        if "fecha_nacimiento" in data:
            est.fecha_nacimiento = datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d")
        if "cedula_identidad" in data: est.cedula_identidad = data["cedula_identidad"]
        if "orden_nacimiento" in data: est.orden_nacimiento = data["orden_nacimiento"]
        models.db.session.commit()
        log_audit(request.user.id_usuario, "ACTUALIZAR_ESTUDIANTE", f"Cedula: {cedula}")
        return jsonify({"message": "Estudiante actualizado correctamente"})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al actualizar estudiante: {str(e)}"}), 500


@api_admin.route("/estudiantes/<cedula>", methods=["DELETE"])
@token_required
def eliminar_estudiante(cedula):
    try:
        est = models.Estudiante.query.get(cedula)
        if not est:
            return jsonify({"message": "Estudiante no encontrado"}), 404
        for ins in est.inscripciones:
            models.db.session.delete(ins)
        models.db.session.delete(est)
        models.db.session.commit()
        log_audit(request.user.id_usuario, "ELIMINAR_ESTUDIANTE", f"Cedula: {cedula}")
        return jsonify({"message": f"Estudiante {cedula} eliminado correctamente"})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al eliminar estudiante: {str(e)}"}), 500


@api_admin.route("/estudiantes", methods=["GET"])
@token_required
def listar_estudiantes():
    search = request.args.get("search", "")
    query = models.Estudiante.query
    if search:
        query = query.filter(
            models.Estudiante.cedula_escolar.contains(search) |
            models.Estudiante.apellidos.contains(search))
    estudiantes = query.all()
    return jsonify([{
        "cedula": e.cedula_escolar,
        "nombre_completo": f"{e.nombres} {e.apellidos}",
        "grado": e.inscripciones[-1].grado.nombre if e.inscripciones else "Sin inscripcion",
    } for e in estudiantes])


# ============================
# INSCRIPCION (admin)
# ============================
@api_admin.route("/inscripcion", methods=["POST"])
@token_required
def inscribir_plantilla():
    data = request.get_json()
    try:
        ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()
        if not ano_activo:
            return jsonify({"message": "No hay ano escolar activo"}), 400
        rep_data = data.get("representante")
        rep = models.Representante.query.filter_by(cedula=rep_data["cedula"]).first()
        if not rep:
            rep = models.Representante(cedula=rep_data["cedula"], nombres=rep_data.get("nombres", ""),
                                       apellidos=rep_data.get("apellidos", ""), telefono=rep_data.get("telefono"),
                                       profesion=rep_data.get("profesion"), direccion_habitacion=rep_data.get("direccion"))
            models.db.session.add(rep)
            models.db.session.flush()
            log_audit(request.user.id_usuario, "REGISTRO_REPRESENTANTE", f"Cedula: {rep.cedula}")
        nueva_inscripcion = models.Inscripcion(
            cedula_escolar=data["cedula_estudiante"], id_representante=rep.id_representante,
            id_grado=data.get("id_grado", 1), id_ano_escolar=ano_activo.id_ano,
            id_usuario=request.user.id_usuario, estado='REGULAR')
        models.db.session.add(nueva_inscripcion)
        models.db.session.commit()
        log_audit(request.user.id_usuario, "INSCRIPCION", f"Est: {data['cedula_estudiante']} - Ano: {ano_activo.periodo}")
        return jsonify({"message": "Ficha de inscripcion guardada exitosamente"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error en inscripcion: {str(e)}"}), 500


# ============================
# ANOS ESCOLARES
# ============================
@api_admin.route("/anos-escolares", methods=["GET", "POST"])
@token_required
def gestionar_anos():
    if request.method == "GET":
        anos = models.AnoEscolar.query.all()
        stats = []
        for ano in anos:
            matricula = models.Inscripcion.query.filter_by(id_ano_escolar=ano.id_ano).count()
            stats.append({"periodo": ano.periodo, "estado": ano.estado, "matricula": matricula})
        return jsonify(stats)
    data = request.get_json()
    nuevo = models.AnoEscolar(periodo=data["periodo"], estado="ACTIVO")
    models.db.session.add(nuevo)
    models.db.session.commit()
    return jsonify({"message": "Ano escolar abierto"}), 201


# ============================
# REPRESENTANTES (admin)
# ============================
@api_admin.route("/representantes", methods=["GET", "POST"])
@token_required
def registro_representante():
    if request.method == "GET":
        search = request.args.get("search", "")
        query = models.Representante.query
        if search:
            query = query.filter(models.Representante.cedula.contains(search) |
                                 models.Representante.apellidos.contains(search) |
                                 models.Representante.nombres.contains(search))
        representantes = query.all()
        return jsonify([{"cedula": r.cedula, "nombres": r.nombres, "apellidos": r.apellidos,
                         "telefono": r.telefono, "email": r.email, "profesion": r.profesion,
                         "direccion": r.direccion_habitacion} for r in representantes])
    data = request.get_json()
    try:
        nuevo_rep = models.Representante(cedula=data['cedula'], nombres=data['nombres'],
                                         apellidos=data['apellidos'], telefono=data.get('telefono'),
                                         email=data.get('email'), profesion=data.get('profesion'),
                                         direccion_habitacion=data.get('direccion'))
        models.db.session.add(nuevo_rep)
        models.db.session.commit()
        if request.user and hasattr(request.user, "id_usuario"):
            log_audit(request.user.id_usuario, "REGISTRO_REPRESENTANTE", f"Cedula: {nuevo_rep.cedula}")
        return jsonify({"message": "Representante guardado"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al guardar representante: {str(e)}"}), 400


@api_admin.route("/representantes/<cedula>", methods=["PUT"])
@token_required
def actualizar_representante(cedula):
    data = request.get_json()
    try:
        rep = models.Representante.query.filter_by(cedula=cedula).first()
        if not rep:
            return jsonify({"message": "Representante no encontrado"}), 404
        if "nombres" in data: rep.nombres = data["nombres"]
        if "apellidos" in data: rep.apellidos = data["apellidos"]
        if "email" in data: rep.email = data["email"]
        if "telefono" in data: rep.telefono = data["telefono"]
        if "profesion" in data: rep.profesion = data["profesion"]
        if "direccion" in data: rep.direccion_habitacion = data["direccion"]
        if "monto_mensual_ingresos" in data: rep.monto_mensual_ingresos = data["monto_mensual_ingresos"]
        models.db.session.commit()
        log_audit(request.user.id_usuario, "ACTUALIZAR_REPRESENTANTE", f"Cedula: {cedula}")
        return jsonify({"message": "Representante actualizado correctamente"})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al actualizar representante: {str(e)}"}), 500


@api_admin.route("/representantes/<cedula>", methods=["DELETE"])
@token_required
def eliminar_representante(cedula):
    try:
        rep = models.Representante.query.filter_by(cedula=cedula).first()
        if not rep:
            return jsonify({"message": "Representante no encontrado"}), 404
        inscripciones = models.Inscripcion.query.filter_by(id_representante=rep.id_representante).count()
        if inscripciones > 0:
            return jsonify({"message": f"No se puede eliminar: tiene {inscripciones} inscripcion(es) asociada(s). Elimine primero las inscripciones."}), 409
        models.db.session.delete(rep)
        models.db.session.commit()
        log_audit(request.user.id_usuario, "ELIMINAR_REPRESENTANTE", f"Cedula: {cedula}")
        return jsonify({"message": f"Representante {cedula} eliminado correctamente"})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al eliminar representante: {str(e)}"}), 500


# ============================
# MATRICULA
# ============================
@api_admin.route("/matricula", methods=["GET"])
@token_required
def ver_matricula():
    ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()
    if not ano_activo:
        return jsonify([])
    inscripciones = models.Inscripcion.query.filter_by(id_ano_escolar=ano_activo.id_ano).all()
    resultado = []
    for ins in inscripciones:
        resultado.append({
            "nombre": f"{ins.estudiante.nombres} {ins.estudiante.apellidos}",
            "cedula": ins.estudiante.cedula_escolar,
            "grado": ins.grado.nombre, "tipo": "regular",
        })
    return jsonify(resultado)
