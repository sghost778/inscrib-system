# security.py - Autenticación por sesión (Flask session)
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import bcrypt
from models import db, RegistroAuditoria, Usuario


# --- UTILIDADES DE HASH ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# --- AUDITORÍA ---
def log_audit(user_id, action, detail=None):
    """Registra una acción en REGISTRO_AUDITORIA.
    Si falla, hace rollback y registra el error en consola sin propagar la excepción."""
    try:
        log = RegistroAuditoria(id_usuario=user_id, accion=action, detalle=detail)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()   # limpia la sesión para no bloquear el flujo principal
        print(f"[AUDIT WARN] No se pudo registrar auditoría ({action}): {e}")


# --- CONTROL DE ACCESO POR SESIÓN ---
def _usuario_actual():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(Usuario, user_id)


def token_required(f):
    """Exige sesión válida para endpoints JSON. Devuelve 401 si no hay sesión."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _usuario_actual()
        if not user:
            return jsonify({"success": False,
                            "message": "Sesión expirada o no iniciada. Inicia sesión nuevamente."}), 401
        request.user = user
        return f(*args, **kwargs)
    return decorated


def login_requerido(f):
    """Exige sesión válida para páginas (render_template). Redirige a /login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _usuario_actual()
        if not user:
            return redirect(url_for('view_login'))
        request.user = user
        return f(*args, **kwargs)
    return decorated
