# security.py – autenticación por JWT (Bearer) con respaldo de sesión
# ----------------------------------------------------------------

import jwt
import datetime
import bcrypt
from functools import wraps
from flask import request, jsonify, session, current_app

import models
from models import db, RegistroAuditoria, Usuario

# --- UTILIDADES DE HASH ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except (ValueError, TypeError):
        return False

# --- AUDITORÍA ---
def log_audit(user_id, action, detail=None):
    """Registra una acción en REGISTRO_AUDITORIA.
    Si falla, hace rollback y registra el error en consola sin propagar la excepción."""
    try:
        log = RegistroAuditoria(id_usuario=user_id, accion=action, detalle=detail)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()   # ← limpia la sesión para no bloquear el flujo principal
        print(f"[AUDIT WARN] No se pudo registrar auditoría ({action}): {e}")

# --- JWT ---
def _secret():
    return current_app.config.get('SECRET_KEY', 'cambia-esto-en-produccion')

def generate_jwt(user, expires_hours=12, tipo='access'):
    payload = {
        'sub': str(user.id_usuario),
        'usuario': user.usuario,
        'rol': getattr(user, 'rol', 'admin'),
        'tipo': tipo,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
    }
    return jwt.encode(payload, _secret(), algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, _secret(), algorithms=['HS256'])
    except Exception:
        return None

def _claims_from_request():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:].strip()
        if token:
            return decode_jwt(token)
    return None

# --- DECORADORES ---
def token_required(f):
    """Exige autenticación: acepta un JWT válido (Bearer) o una sesión activa."""
    @wraps(f)
    def decorated(*args, **kwargs):
        claims = _claims_from_request()
        if claims and claims.get('sub'):
            user = db.session.get(Usuario, int(claims['sub']))
            if user:
                request.user = user
                request.jwt_claims = claims
                return f(*args, **kwargs)
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(Usuario, user_id)
            if user:
                request.user = user
                return f(*args, **kwargs)
        return jsonify({"success": False, "message": "No autenticado"}), 401
    return decorated

def portal_token_required(f):
    """Exige sesión de representante: acepta JWT de tipo 'portal' o sesión activa."""
    @wraps(f)
    def decorated(*args, **kwargs):
        claims = _claims_from_request()
        if claims and claims.get('tipo') == 'portal':
            user = db.session.get(Usuario, int(claims.get('sub')))
            if user:
                representante = models.Representante.query.filter_by(cedula=user.usuario).first()
                if representante:
                    request.portal_rep = representante
                    request.portal_rep_cedula = representante.cedula
                    return f(*args, **kwargs)
        cedula = session.get('portal_rep_cedula')
        if cedula:
            representante = models.Representante.query.filter_by(cedula=cedula).first()
            if representante:
                request.portal_rep = representante
                request.portal_rep_cedula = cedula
                return f(*args, **kwargs)
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401
    return decorated
