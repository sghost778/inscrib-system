from datetime import datetime
import secrets
from flask import Blueprint, jsonify, request, session

import models
from security import check_password, log_audit, token_required

api = Blueprint("api", __name__)


# ============================
# HELPER: SESIÓN Y RESPUESTA
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

    log_audit(uid, "LOGIN", "Inicio de sesión exitoso")

    return jsonify({"success": True, "usuario": nombre, "rol": rol, "token": secrets.token_hex(16)})


# ============================
# LOGIN
# ============================
@api.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    if not data and request.form:
        data = {"usuario": request.form.get("usuario"), "password": request.form.get("password")}
    usuario = (data.get("usuario") or "admin").strip()

    try:
        models.db.session.rollback()
        user = models.Usuario.query.filter_by(usuario=usuario).first()
        
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

        if not check_password(password, user.password_hash):
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401

        return _hacer_sesion_y_responder(user)

    except Exception as e:
        import traceback
        traceback.print_exc()
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error en servidor: {str(e)}"}), 500


# ============================
# LOGOUT
# ============================
@api.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ============================
# LOGS
# ============================
@api.route("/dashboard/logs", methods=["GET"])
@token_required
def get_logs():
    logs = (
        models.RegistroAuditoria.query.order_by(models.RegistroAuditoria.fecha_hora.desc())
        .limit(10)
        .all()
    )

    resultado = []
    for log in logs:
        resultado.append(
            {
                "usuario": log.usuario.usuario,
                "nombre": f"{log.usuario.nombre} {log.usuario.apellido}",
                "fecha": log.fecha_hora.strftime("%d/%m/%Y"),
                "hora": log.fecha_hora.strftime("%I:%M %p"),
                "accion": log.accion,
            }
        )
    return jsonify(resultado)


# ============================
# USUARIOS CRUD
# ============================
@api.route("/usuarios", methods=["GET"])
@token_required
def listar_usuarios():
    usuarios = models.Usuario.query.all()
    return jsonify({
        "success": True,
        "usuarios": [{
            "id_usuario": u.id_usuario,
            "nombre_completo": f"{u.nombre or ''} {u.apellido or ''}".strip() or u.usuario,
            "usuario": u.usuario,
            "rol": getattr(u, 'rol', 'admin'),
            "estado": "activo"
        } for u in usuarios]
    })

@api.route("/usuarios", methods=["POST"])
@token_required
def crear_usuario():
    data = request.get_json()
    exists = models.Usuario.query.filter_by(usuario=data["usuario"]).first()
    if exists:
        return jsonify({"success": False, "message": "El usuario ya existe"}), 400
    from security import hash_password
    u = models.Usuario(
        nombre=data.get("nombre", ""),
        apellido=data.get("apellido", ""),
        usuario=data["usuario"],
        password_hash=hash_password(data["password"]),
        rol=data.get("rol", "secretario")
    )
    models.db.session.add(u)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Usuario creado correctamente"}), 201

@api.route("/usuarios/<int:id>", methods=["PUT"])
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

@api.route("/usuarios/<int:id>", methods=["DELETE"])
@token_required
def eliminar_usuario(id):
    u = models.Usuario.query.get_or_404(id)
    if u.usuario == 'admin':
        return jsonify({"success": False, "message": "No se puede eliminar el usuario admin"}), 400
    models.db.session.delete(u)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Usuario eliminado"})


# ============================
# SITE CONFIG (CLAVE-VALOR)
# ============================
@api.route("/site-config", methods=["GET"])
def get_site_config():
    configs = models.SiteConfig.query.all()
    return jsonify({c.key: c.value for c in configs})

@api.route("/site-config", methods=["PUT"])
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
# NOTICIAS
# ============================
@api.route("/noticias", methods=["GET", "POST"])
def noticias():
    if request.method == "GET":
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
    data = request.get_json()
    n = models.Noticia(titulo=data["titulo"], resumen=data.get("resumen"),
                       contenido=data.get("contenido"), imagen=data.get("imagen"))
    models.db.session.add(n)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Noticia creada"}), 201

@api.route("/noticias/<int:id>", methods=["PUT", "DELETE"])
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
# PROGRAMAS ACADÉMICOS
# ============================
@api.route("/programas", methods=["GET", "POST"])
def programas():
    if request.method == "GET":
        programas = models.ProgramaAcademico.query.filter_by(activo=True).all()
        return jsonify([{
            "id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
            "nivel": p.nivel, "icono": p.icono
        } for p in programas])
    data = request.get_json()
    p = models.ProgramaAcademico(nombre=data["nombre"], descripcion=data.get("descripcion"),
                                  nivel=data.get("nivel"), icono=data.get("icono", "fa-book"))
    models.db.session.add(p)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Programa creado"}), 201

@api.route("/programas/<int:id>", methods=["PUT", "DELETE"])
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
# GALERÍA
# ============================
@api.route("/galeria", methods=["GET", "POST"])
def galeria():
    if request.method == "GET":
        imagenes = models.Galeria.query.order_by(models.Galeria.fecha_subida.desc()).all()
        return jsonify([{
            "id": g.id, "titulo": g.titulo, "imagen": g.imagen,
            "descripcion": g.descripcion,
            "fecha": g.fecha_subida.strftime("%d/%m/%Y") if g.fecha_subida else ""
        } for g in imagenes])
    data = request.get_json()
    g = models.Galeria(titulo=data.get("titulo"), imagen=data["imagen"],
                        descripcion=data.get("descripcion"))
    models.db.session.add(g)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Imagen agregada"}), 201

@api.route("/galeria/<int:id>", methods=["DELETE"])
@token_required
def galeria_id(id):
    g = models.Galeria.query.get_or_404(id)
    models.db.session.delete(g)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Imagen eliminada"})


# ============================
# MENSAJES DE CONTACTO
# ============================
@api.route("/contacto", methods=["POST"])
def contacto_publico():
    data = request.get_json()
    m = models.MensajeContacto(nombre=data["nombre"], email=data["email"],
                                telefono=data.get("telefono"), mensaje=data["mensaje"])
    models.db.session.add(m)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Mensaje enviado correctamente"}), 201

@api.route("/mensajes", methods=["GET"])
@token_required
def mensajes():
    msgs = models.MensajeContacto.query.order_by(models.MensajeContacto.fecha.desc()).all()
    return jsonify([{
        "id": m.id, "nombre": m.nombre, "email": m.email,
        "telefono": m.telefono, "mensaje": m.mensaje,
        "fecha": m.fecha.strftime("%d/%m/%Y %I:%M %p") if m.fecha else "",
        "leido": m.leido
    } for m in msgs])

@api.route("/mensajes/<int:id>/leer", methods=["PUT"])
@token_required
def mensaje_leer(id):
    m = models.MensajeContacto.query.get_or_404(id)
    m.leido = True
    models.db.session.commit()
    return jsonify({"success": True})


# ============================
# CREAR ESTUDIANTE
# ============================
@api.route("/estudiantes", methods=["POST"])
@token_required
def crear_estudiante():
    data = request.get_json()
    try:
        nuevo_est = models.Estudiante(
            cedula_escolar=data["cedula_escolar"],
            cedula_identidad=data.get("cedula_identidad"),
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            fecha_nacimiento=datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d"),
            orden_nacimiento=data.get("orden_nacimiento")
        )

        models.db.session.add(nuevo_est)
        models.db.session.commit()

        log_audit(
            request.user.id_usuario,
            "REGISTRO_ESTUDIANTE",
            f"Cédula: {nuevo_est.cedula_escolar}",
        )

        return jsonify({"message": "Estudiante registrado correctamente"}), 201

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al registrar estudiante: {str(e)}"}), 500


# ============================
# ACTUALIZAR ESTUDIANTE
# ============================
@api.route("/estudiantes/<cedula>", methods=["PUT"])
@token_required
def actualizar_estudiante(cedula):
    """Actualiza datos de un estudiante. Solo actualiza los campos enviados."""
    data = request.get_json()
    try:
        est = models.Estudiante.query.get(cedula)
        if not est:
            return jsonify({"message": "Estudiante no encontrado"}), 404

        if "nombres" in data:
            est.nombres = data["nombres"]
        if "apellidos" in data:
            est.apellidos = data["apellidos"]
        if "fecha_nacimiento" in data:
            est.fecha_nacimiento = datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d")
        if "cedula_identidad" in data:
            est.cedula_identidad = data["cedula_identidad"]
        if "orden_nacimiento" in data:
            est.orden_nacimiento = data["orden_nacimiento"]

        models.db.session.commit()
        log_audit(request.user.id_usuario, "ACTUALIZAR_ESTUDIANTE", f"Cédula: {cedula}")
        return jsonify({"message": "Estudiante actualizado correctamente"})

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al actualizar estudiante: {str(e)}"}), 500


# ============================
# ELIMINAR ESTUDIANTE
# ============================
@api.route("/estudiantes/<cedula>", methods=["DELETE"])
@token_required
def eliminar_estudiante(cedula):
    """Elimina un estudiante. Primero elimina sus inscripciones para no romper llaves foráneas."""
    try:
        est = models.Estudiante.query.get(cedula)
        if not est:
            return jsonify({"message": "Estudiante no encontrado"}), 404

        # Eliminar inscripciones relacionadas primero
        for ins in est.inscripciones:
            models.db.session.delete(ins)

        models.db.session.delete(est)
        models.db.session.commit()
        log_audit(request.user.id_usuario, "ELIMINAR_ESTUDIANTE", f"Cédula: {cedula}")
        return jsonify({"message": f"Estudiante {cedula} eliminado correctamente"})

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al eliminar estudiante: {str(e)}"}), 500



# ============================
# LISTAR ESTUDIANTES
# ============================
@api.route("/estudiantes", methods=["GET"])
@token_required
def listar_estudiantes():
    search = request.args.get("search", "")
    query = models.Estudiante.query

    if search:
        query = query.filter(
            models.Estudiante.cedula_escolar.contains(search)
            | models.Estudiante.apellidos.contains(search)
        )

    estudiantes = query.all()

    return jsonify(
        [
            {
                "cedula": e.cedula_escolar,
                "nombre_completo": f"{e.nombres} {e.apellidos}",
                "grado": e.inscripciones[-1].grado.nombre if e.inscripciones else "Sin inscripción",
            }
            for e in estudiantes
        ]
    )



# ============================
# INSCRIPCIÓN
# ============================
@api.route("/inscripcion", methods=["POST"])
@token_required
def inscribir_plantilla():
    data = request.get_json()

    try:
        ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()
        if not ano_activo:
            return jsonify({"message": "No hay año escolar activo"}), 400

        rep_data = data.get("representante")
        rep = models.Representante.query.filter_by(cedula=rep_data["cedula"]).first()

        if not rep:
            rep = models.Representante(
                cedula=rep_data["cedula"],
                nombres=rep_data.get("nombres", ""),
                apellidos=rep_data.get("apellidos", ""),
                telefono=rep_data.get("telefono"),
                profesion=rep_data.get("profesion"),
                direccion_habitacion=rep_data.get("direccion")
            )
            models.db.session.add(rep)
            models.db.session.flush()

            log_audit(
                request.user.id_usuario,
                "REGISTRO_REPRESENTANTE",
                f"Cédula: {rep.cedula}",
            )

        nueva_inscripcion = models.Inscripcion(
            cedula_escolar=data["cedula_estudiante"],
            id_representante=rep.id_representante,
            id_grado=data.get("id_grado", 1),
            id_ano_escolar=ano_activo.id_ano,
            id_usuario=request.user.id_usuario,
            estado='REGULAR'
        )

        models.db.session.add(nueva_inscripcion)
        models.db.session.commit()

        log_audit(
            request.user.id_usuario,
            "INSCRIPCION",
            f"Est: {data['cedula_estudiante']} - Año: {ano_activo.periodo}",
        )

        return jsonify({"message": "Ficha de inscripción guardada exitosamente"}), 201

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error en inscripción: {str(e)}"}), 500



# ============================
# AÑOS ESCOLARES
# ============================
@api.route("/anos-escolares", methods=["GET", "POST"])
@token_required
def gestionar_anos():
    if request.method == "GET":
        anos = models.AnoEscolar.query.all()
        stats = []

        for ano in anos:
            matricula = models.Inscripcion.query.filter_by(id_ano_escolar=ano.id_ano).count()
            stats.append(
                {"periodo": ano.periodo, "estado": ano.estado, "matricula": matricula}
            )

        return jsonify(stats)

    data = request.get_json()
    nuevo = models.AnoEscolar(periodo=data["periodo"], estado="ACTIVO")
    models.db.session.add(nuevo)
    models.db.session.commit()

    return jsonify({"message": "Año escolar abierto"}), 201



# ============================
# REGISTRO Y LISTADO DE REPRESENTANTE
# ============================
@api.route("/representantes", methods=["GET", "POST"])
@token_required
def registro_representante():
    if request.method == "GET":
        search = request.args.get("search", "")
        query = models.Representante.query

        if search:
            query = query.filter(
                models.Representante.cedula.contains(search)
                | models.Representante.apellidos.contains(search)
                | models.Representante.nombres.contains(search)
            )

        representantes = query.all()
        return jsonify(
            [
                {
                    "cedula": r.cedula,
                    "nombres": r.nombres,
                    "apellidos": r.apellidos,
                    "telefono": r.telefono,
                    "email": r.email,
                    "profesion": r.profesion,
                    "direccion": r.direccion_habitacion
                }
                for r in representantes
            ]
        )

    # POST (Crear Nuevo)
    data = request.get_json()
    try:
        nuevo_rep = models.Representante(
            cedula=data['cedula'],
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            telefono=data.get('telefono'),
            email=data.get('email'),
            profesion=data.get('profesion'),
            direccion_habitacion=data.get('direccion')
        )

        models.db.session.add(nuevo_rep)
        models.db.session.commit()

        # Solo audita si hay un usuario real, para evitar errores en modo sin seguridad (FakeUser)
        if request.user and hasattr(request.user, "id_usuario"):
            log_audit(
                request.user.id_usuario,
                "REGISTRO_REPRESENTANTE",
                f"Cédula: {nuevo_rep.cedula}",
            )

        return jsonify({"message": "Representante guardado"}), 201

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al guardar representante: {str(e)}"}), 400


# ============================
# ACTUALIZAR REPRESENTANTE
# ============================
@api.route("/representantes/<cedula>", methods=["PUT"])
@token_required
def actualizar_representante(cedula):
    """Actualiza datos de un representante sin tocar la cédula (llave primaria/única)."""
    data = request.get_json()
    try:
        rep = models.Representante.query.filter_by(cedula=cedula).first()
        if not rep:
            return jsonify({"message": "Representante no encontrado"}), 404

        # Actualizar solo los campos presentes en el body (no tocar la cédula)
        if "nombres" in data:
            rep.nombres = data["nombres"]
        if "apellidos" in data:
            rep.apellidos = data["apellidos"]
        if "email" in data:
            rep.email = data["email"]
        if "telefono" in data:
            rep.telefono = data["telefono"]
        if "profesion" in data:
            rep.profesion = data["profesion"]
        if "direccion" in data:
            rep.direccion_habitacion = data["direccion"]
        if "monto_mensual_ingresos" in data:
            rep.monto_mensual_ingresos = data["monto_mensual_ingresos"]

        models.db.session.commit()
        log_audit(request.user.id_usuario, "ACTUALIZAR_REPRESENTANTE", f"Cédula: {cedula}")
        return jsonify({"message": "Representante actualizado correctamente"})

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al actualizar representante: {str(e)}"}), 500


# ============================
# ELIMINAR REPRESENTANTE
# ============================
@api.route("/representantes/<cedula>", methods=["DELETE"])
@token_required
def eliminar_representante(cedula):
    """Elimina un representante. No se puede eliminar si tiene inscripciones activas."""
    try:
        rep = models.Representante.query.filter_by(cedula=cedula).first()
        if not rep:
            return jsonify({"message": "Representante no encontrado"}), 404

        # Verificar que no tenga inscripciones activas antes de eliminar
        inscripciones = models.Inscripcion.query.filter_by(id_representante=rep.id_representante).count()
        if inscripciones > 0:
            return jsonify({
                "message": f"No se puede eliminar: tiene {inscripciones} inscripción(es) asociada(s). "
                           "Elimine primero las inscripciones."
            }), 409

        models.db.session.delete(rep)
        models.db.session.commit()
        log_audit(request.user.id_usuario, "ELIMINAR_REPRESENTANTE", f"Cédula: {cedula}")
        return jsonify({"message": f"Representante {cedula} eliminado correctamente"})

    except Exception as e:
        models.db.session.rollback()
        return jsonify({"message": f"Error al eliminar representante: {str(e)}"}), 500



# ============================
# PORTAL REPRESENTANTE (PÚBLICO)
# ============================

@api.route("/portal/registro", methods=["POST"])
def portal_registro():
    """Registro público de representante. Crea Usuario + Representante."""
    data = request.get_json()
    if not data or not data.get('cedula') or not data.get('password'):
        return jsonify({"success": False, "message": "Cédula y contraseña requeridas"}), 400
    try:
        cedula = data['cedula'].strip()
        if models.Representante.query.filter_by(cedula=cedula).first():
            return jsonify({"success": False, "message": "Ya existe un representante con esta cédula"}), 400
        if models.Usuario.query.filter_by(usuario=cedula).first():
            return jsonify({"success": False, "message": "Este usuario ya está registrado"}), 400

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

        user = models.Usuario(
            nombre=rep.nombres,
            apellido=rep.apellidos,
            usuario=cedula,
            password_hash=__import__('security').hash_password(data['password']),
            rol='representante'
        )
        models.db.session.add(user)
        models.db.session.commit()

        return jsonify({"success": True, "message": "Registro exitoso. Ya puedes iniciar sesión."}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error al registrar: {str(e)}"}), 500


@api.route("/portal/login", methods=["POST"])
def portal_login():
    """Login para representantes."""
    data = request.get_json()
    cedula = (data.get('usuario') or '').strip()
    password = data.get('password', '')
    if not cedula or not password:
        return jsonify({"success": False, "message": "Cédula y contraseña requeridas"}), 400

    user = models.Usuario.query.filter_by(usuario=cedula, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

    from security import check_password
    if not check_password(password, user.password_hash):
        return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401

    rep = models.Representante.query.filter_by(cedula=cedula).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404

    session['portal_rep_cedula'] = rep.cedula
    session['portal_rep_nombre'] = f"{rep.nombres} {rep.apellidos}"
    session['portal_rep_id'] = rep.id_representante

    return jsonify({
        "success": True,
        "nombre": f"{rep.nombres} {rep.apellidos}",
        "cedula": rep.cedula
    })


@api.route("/portal/logout", methods=["POST"])
def portal_logout():
    session.pop('portal_rep_cedula', None)
    session.pop('portal_rep_nombre', None)
    session.pop('portal_rep_id', None)
    return jsonify({"success": True})


@api.route("/portal/sesion", methods=["GET"])
def portal_sesion():
    cedula = session.get('portal_rep_cedula')
    nombre = session.get('portal_rep_nombre')
    if cedula and nombre:
        return jsonify({"autenticado": True, "nombre": nombre, "cedula": cedula})
    return jsonify({"autenticado": False})


@api.route("/portal/grados", methods=["GET"])
def portal_grados():
    grados = models.Grado.query.all()
    return jsonify([{"id": g.id_grado, "nombre": g.nombre, "nivel": g.nivel} for g in grados])


@api.route("/portal/estudiantes", methods=["POST"])
def portal_crear_estudiante():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401

    data = request.get_json()
    cedula_escolar = data.get("cedula_escolar", "").strip()
    if not cedula_escolar:
        return jsonify({"success": False, "message": "Cédula escolar es requerida"}), 400
    if models.Estudiante.query.get(cedula_escolar):
        return jsonify({"success": False, "message": "Ya existe un estudiante con esta cédula escolar"}), 400
    ci = data.get("cedula_identidad", "").strip()
    if ci and models.Estudiante.query.filter_by(cedula_identidad=ci).first():
        return jsonify({"success": False, "message": "Ya existe un estudiante con esta cédula de identidad"}), 400
    try:
        from datetime import datetime
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
        return jsonify({"success": False, "message": f"Error al registrar: verifica los datos ingresados"}), 400


@api.route("/portal/estudiantes", methods=["GET"])
def portal_mis_estudiantes():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
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


@api.route("/portal/inscripcion", methods=["POST"])
def portal_inscribir():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    data = request.get_json()
    try:
        ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()
        if not ano_activo:
            return jsonify({"success": False, "message": "No hay año escolar activo"}), 400

        rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
        if not rep:
            return jsonify({"success": False, "message": "Representante no encontrado"}), 404

        estudiante = models.Estudiante.query.get(data["cedula_escolar"])
        if not estudiante:
            return jsonify({"success": False, "message": "Estudiante no encontrado. Regístralo primero."}), 404

        existe = models.Inscripcion.query.filter_by(
            cedula_escolar=data["cedula_escolar"],
            id_ano_escolar=ano_activo.id_ano
        ).first()
        if existe:
            return jsonify({"success": False, "message": "Este estudiante ya está inscrito en el año escolar activo"}), 400

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
        return jsonify({"success": True, "message": "Inscripción realizada exitosamente"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@api.route("/portal/perfil", methods=["GET", "PUT"])
def portal_perfil():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404
    if request.method == "GET":
        return jsonify({
            "cedula": rep.cedula,
            "nombres": rep.nombres,
            "apellidos": rep.apellidos,
            "email": rep.email or "",
            "telefono": rep.telefono or "",
            "direccion": rep.direccion_habitacion or ""
        })
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


@api.route("/portal/password", methods=["PUT"])
def portal_password():
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    data = request.get_json()
    current = data.get('current', '')
    new_pass = data.get('new_password', '')
    if not current or not new_pass:
        return jsonify({"success": False, "message": "Contraseña actual y nueva requeridas"}), 400
    if len(new_pass) < 4:
        return jsonify({"success": False, "message": "La nueva contraseña debe tener al menos 4 caracteres"}), 400
    user = models.Usuario.query.filter_by(usuario=cedula_rep, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    from security import check_password, hash_password
    if not check_password(current, user.password_hash):
        return jsonify({"success": False, "message": "Contraseña actual incorrecta"}), 401
    user.password_hash = hash_password(new_pass)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Contraseña cambiada exitosamente"})


@api.route("/portal/recuperar", methods=["POST"])
def portal_recuperar():
    cedula = (request.get_json() or {}).get('cedula', '').strip()
    if not cedula:
        return jsonify({"success": False, "message": "Ingresa tu cédula"}), 400
    user = models.Usuario.query.filter_by(usuario=cedula, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "No se encontró una cuenta con esta cédula"}), 404
    return jsonify({"success": True, "message": "Tu cédula está registrada. Contacta a la institución para restablecer tu contraseña o usa la opción de cambio desde tu perfil."})


@api.route("/portal/constancia/<cedula_escolar>", methods=["GET"])
def portal_constancia(cedula_escolar):
    cedula_rep = session.get('portal_rep_cedula')
    if not cedula_rep:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
    if not rep:
        return jsonify({"success": False, "message": "Representante no encontrado"}), 404
    inscripcion = models.Inscripcion.query.filter_by(
        cedula_escolar=cedula_escolar,
        id_representante=rep.id_representante
    ).first()
    if not inscripcion:
        return jsonify({"success": False, "message": "Inscripción no encontrada"}), 404
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


# ============================
# MATRÍCULA (admin)
# ============================
@api.route("/matricula", methods=["GET"])
@token_required
def ver_matricula():
    ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()

    if not ano_activo:
        return jsonify([])

    inscripciones = models.Inscripcion.query.filter_by(id_ano_escolar=ano_activo.id_ano).all()

    resultado = []
    for ins in inscripciones:
        resultado.append(
            {
                "nombre": f"{ins.estudiante.nombres} {ins.estudiante.apellidos}",
                "cedula": ins.estudiante.cedula_escolar,
                "grado": ins.grado.nombre,
                "tipo": "regular",
            }
        )

    return jsonify(resultado)
