# security.py – VERSIÓN SIN JWT PARA DEMO
# ----------------------------------------

from functools import wraps
from flask import request, jsonify
import bcrypt
from models import db, RegistroAuditoria, Usuario

# --- UTILIDADES DE HASH (SE MANTIENEN) ---
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
        db.session.rollback()   # ← limpia la sesión para no bloquear el flujo principal
        print(f"[AUDIT WARN] No se pudo registrar auditoría ({action}): {e}")

from flask import session

# --- TOKEN DESACTIVADO ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id', 1)
        user = db.session.get(Usuario, user_id)
        
        if not user:
            class FakeUser:
                id_usuario = 1
                usuario = "admin"
                nombre = "Usuario"
                apellido = "Invitado"
                rol = "admin"
            user = FakeUser()

        request.user = user
        return f(*args, **kwargs)
    return decorated
