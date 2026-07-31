from datetime import datetime
from io import BytesIO
from flask import Blueprint, jsonify, request, session, Response

import models
from security import hash_password, check_password, generate_jwt, portal_token_required

api_public = Blueprint("api_public", __name__)


@api_public.route("/registro", methods=["POST"])
def registro_usuario():
    """Registro público de cuentas de personal (secretario/docente)."""
    data = request.get_json()
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password", "")
    if not nombre or not apellido or not usuario or not password:
        return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400
    if models.Usuario.query.filter_by(usuario=usuario).first():
        return jsonify({"success": False, "message": "El usuario ya existe"}), 400
    from security import hash_password
    u = models.Usuario(
        nombre=nombre,
        apellido=apellido,
        usuario=usuario,
        password_hash=hash_password(password),
        rol=data.get("rol", "secretario")
    )
    models.db.session.add(u)
    models.db.session.commit()
    return jsonify({"success": True, "message": "Usuario registrado correctamente"}), 201


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
    if not data or not (data.get("nombre") or "").strip() or not (data.get("email") or "").strip() or not (data.get("mensaje") or "").strip():
        return jsonify({"success": False, "message": "Nombre, email y mensaje son requeridos"}), 400
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

        return jsonify({"success": True, "message": "Registro exitoso. Ya puedes iniciar sesión."}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error al registrar: {str(e)}"}), 500


@api_public.route("/portal/login", methods=["POST"])
def portal_login():
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

    token = generate_jwt(user, tipo='portal') if user else None
    return jsonify({"success": True, "nombre": f"{rep.nombres} {rep.apellidos}",
                    "cedula": rep.cedula, "token": token})


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
@portal_token_required
def portal_crear_estudiante():
    cedula_rep = request.portal_rep_cedula
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Datos no recibidos"}), 400
    cedula_escolar = (data.get("cedula_escolar") or "").strip()
    nombres = (data.get("nombres") or "").strip()
    apellidos = (data.get("apellidos") or "").strip()
    fecha = (data.get("fecha_nacimiento") or "").strip()
    if not cedula_escolar or not nombres or not apellidos or not fecha:
        return jsonify({"success": False, "message": "Cédula escolar, nombres, apellidos y fecha de nacimiento son requeridos"}), 400
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "message": "La fecha de nacimiento no es válida (use AAAA-MM-DD)"}), 400
    if models.Estudiante.query.get(cedula_escolar):
        return jsonify({"success": False, "message": "Ya existe un estudiante con esta cédula escolar"}), 400
    ci = (data.get("cedula_identidad") or "").strip()
    if ci and models.Estudiante.query.filter_by(cedula_identidad=ci).first():
        return jsonify({"success": False, "message": "Ya existe un estudiante con esta cédula de identidad"}), 400
    try:
        orden = data.get("orden_nacimiento")
        orden = int(orden) if orden not in (None, "") else None
        nuevo_est = models.Estudiante(
            cedula_escolar=cedula_escolar,
            cedula_identidad=ci or None,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_dt,
            orden_nacimiento=orden
        )
        models.db.session.add(nuevo_est)
        models.db.session.commit()
        return jsonify({"success": True, "message": "Estudiante registrado correctamente"}), 201
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": "Error al registrar: verifica los datos ingresados"}), 400


@api_public.route("/portal/estudiantes", methods=["GET"])
@portal_token_required
def portal_mis_estudiantes():
    cedula_rep = request.portal_rep_cedula
    rep = request.portal_rep
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
@portal_token_required
def portal_inscribir():
    cedula_rep = request.portal_rep_cedula
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Datos no recibidos"}), 400
    cedula_escolar = (data.get("cedula_escolar") or "").strip()
    if not cedula_escolar:
        return jsonify({"success": False, "message": "Cédula escolar es requerida"}), 400
    try:
        id_grado = int(data.get("id_grado", 1))
        ano_activo = models.AnoEscolar.query.filter_by(estado="ACTIVO").first()
        if not ano_activo:
            return jsonify({"success": False, "message": "No hay año escolar activo"}), 400
        rep = models.Representante.query.filter_by(cedula=cedula_rep).first()
        if not rep:
            return jsonify({"success": False, "message": "Representante no encontrado"}), 404
        estudiante = models.Estudiante.query.get(cedula_escolar)
        if not estudiante:
            return jsonify({"success": False, "message": "Estudiante no encontrado. Regístralo primero."}), 404
        existe = models.Inscripcion.query.filter_by(
            cedula_escolar=cedula_escolar, id_ano_escolar=ano_activo.id_ano
        ).first()
        if existe:
            return jsonify({"success": False, "message": "Este estudiante ya está inscrito en el año escolar activo"}), 400
        inscripcion = models.Inscripcion(
            cedula_escolar=cedula_escolar,
            id_representante=rep.id_representante,
            id_grado=id_grado,
            id_ano_escolar=ano_activo.id_ano,
            id_usuario=1,
            estado='REGULAR'
        )
        models.db.session.add(inscripcion)
        models.db.session.commit()
        return jsonify({"success": True, "message": "Inscripción realizada exitosamente"}), 201
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "El grado seleccionado no es válido"}), 400
    except Exception as e:
        models.db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@api_public.route("/portal/perfil", methods=["GET", "PUT"])
@portal_token_required
def portal_perfil():
    cedula_rep = request.portal_rep_cedula
    rep = request.portal_rep
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
@portal_token_required
def portal_password():
    cedula_rep = request.portal_rep_cedula
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


@api_public.route("/portal/recuperar", methods=["POST"])
def portal_recuperar():
    cedula = (request.get_json() or {}).get('cedula', '').strip()
    if not cedula:
        return jsonify({"success": False, "message": "Ingresa tu cédula"}), 400
    user = models.Usuario.query.filter_by(usuario=cedula, rol='representante').first()
    if not user:
        return jsonify({"success": False, "message": "No se encontró una cuenta con esta cédula"}), 404
    return jsonify({"success": True, "message": "Tu cédula está registrada. Contacta a la institución para restablecer tu contraseña o usa la opción de cambio desde tu perfil."})


@api_public.route("/portal/constancia/<cedula_escolar>", methods=["GET"])
@portal_token_required
def portal_constancia(cedula_escolar):
    cedula_rep = request.portal_rep_cedula
    rep = request.portal_rep
    inscripcion = models.Inscripcion.query.filter_by(
        cedula_escolar=cedula_escolar, id_representante=rep.id_representante
    ).first()
    if not inscripcion:
        return jsonify({"success": False, "message": "Inscripción no encontrada"}), 404
    est = inscripcion.estudiante

    from models import SiteConfig
    from xml.sax.saxutils import escape
    _n = SiteConfig.query.filter_by(key='nombre_institucion').first()
    inst_name = escape(_n.value) if _n else "Dr. Jos&eacute; Manuel Cova Maza"

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    datos = {
        "estudiante": f"{est.nombres} {est.apellidos}",
        "cedula_escolar": est.cedula_escolar,
        "grado": inscripcion.grado.nombre if inscripcion.grado else "N/A",
        "periodo": inscripcion.ano_escolar.periodo if inscripcion.ano_escolar else "N/A",
        "estado": inscripcion.estado or "REGULAR",
        "fecha": inscripcion.fecha_inscripcion.strftime("%d/%m/%Y") if inscripcion.fecha_inscripcion else "",
        "representante": f"{rep.nombres} {rep.apellidos}",
        "rep_cedula": rep.cedula,
    }

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            topMargin=2.5 * cm, bottomMargin=2.5 * cm,
                            leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                            title="Constancia de Inscripcion")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Centro", parent=styles["Title"], alignment=1))
    styles.add(ParagraphStyle(name="CentroSub", parent=styles["Normal"], alignment=1, textColor=colors.HexColor("#555555")))
    styles.add(ParagraphStyle(name="Etiqueta", parent=styles["Normal"], fontName="Helvetica-Bold"))

    contenido = []
    contenido.append(Paragraph("UNIDAD EDUCATIVA", styles["Centro"]))
    contenido.append(Paragraph(inst_name, styles["Centro"]))
    contenido.append(Paragraph("CONSTANCIA DE INSCRIPCI&Oacute;N", styles["CentroSub"]))
    contenido.append(Spacer(1, 1.2 * cm))

    filas = [
        ["Estudiante:", datos["estudiante"]],
        ["Cédula Escolar:", datos["cedula_escolar"]],
        ["Grado:", datos["grado"]],
        ["Período Escolar:", datos["periodo"]],
        ["Estado:", datos["estado"]],
        ["Fecha de Inscripción:", datos["fecha"]],
        ["Representante:", datos["representante"]],
        ["Cédula del Representante:", datos["rep_cedula"]],
    ]
    tabla = Table([[Paragraph(f, styles["Etiqueta"]), Paragraph(v, styles["Normal"])] for f, v in filas],
                  colWidths=[6 * cm, 10 * cm])
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ]))
    contenido.append(tabla)
    contenido.append(Spacer(1, 2.5 * cm))
    contenido.append(Paragraph("_______________________________", styles["Centro"]))
    contenido.append(Paragraph("Directivo / Secretaria", styles["CentroSub"]))
    contenido.append(Paragraph("Sello de la Institución", styles["CentroSub"]))

    doc.build(contenido)
    pdf = buffer.getvalue()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=constancia_{datos['cedula_escolar']}.pdf"},
    )
