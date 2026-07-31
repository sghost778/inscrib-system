"""
Prueba de humo end-to-end del sistema INSCRIB (modo producción / app_combined).

Cómo ejecutar (desde la raíz del proyecto):
    python tests/test_sistema.py

El test usa una base de datos SQLite temporal (aislada) vía DATABASE_URL, por lo que
NO toca la base de datos real (test.db). Requiere el entorno virtual activado.
"""

import os
import sys
import tempfile

# --- Aislar la base de datos y fijar SECRET_KEY ANTES de importar la app ---
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

_TMP_DB = os.path.join(tempfile.gettempdir(), "inscrib_test_suite.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["DATABASE_URL"] = "sqlite:///" + _TMP_DB
os.environ["SECRET_KEY"] = "test-suite-secret-key-please-change-in-production-1234567890"

import app_combined as A  # noqa: E402  (debe importarse tras fijar el env)

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

results = []


def chk(name, cond, extra=""):
    results.append((name, bool(cond)))
    mark = "[OK ]" if cond else "[FAIL]"
    line = f"{mark} {name}"
    if not cond and extra:
        line += f"  -> {extra}"
    print(line)


def run():
    app = A.app
    c = app.test_client()

    # ---------- PÚBLICO (sin autenticación) ----------
    for path in ("/", "/portal", "/registro", "/recuperar"):
        chk(f"public GET {path}", c.get(path).status_code == 200)

    for api in ("/api/site-config", "/api/noticias", "/api/programas", "/api/galeria"):
        chk(f"public API {api}", c.get(api).status_code == 200)

    chk("admin API sin token -> 401",
        app.test_client().get("/api/estudiantes").status_code == 401)

    # ---------- ADMIN (JWT Bearer) ----------
    r = c.post("/api/login", json={"usuario": ADMIN_USER, "password": ADMIN_PASS})
    chk("admin login", r.status_code == 200, r.get_data(as_text=True)[:120])
    atok = (r.get_json() or {}).get("token")
    chk("admin login devuelve JWT", bool(atok))

    for api in ("/api/estudiantes", "/api/anos-escolares", "/api/usuarios", "/api/dashboard/logs"):
        chk(f"admin API {api} con Bearer",
            c.get(api, headers={"Authorization": f"Bearer {atok}"}).status_code == 200)

    # Crear representante desde admin -> también crea login de portal (clave = cédula)
    import uuid
    _uid = uuid.uuid4().hex[:8]
    rep_cedula = "V-R" + _uid
    r = c.post("/api/representantes",
               json={"cedula": rep_cedula, "nombres": "Rep", "apellidos": "Admin", "email": "r@a.com"},
               headers={"Authorization": f"Bearer {atok}"})
    chk("admin crea representante", r.status_code == 201, r.get_json())
    rp = c.post("/api/portal/login", json={"usuario": rep_cedula, "password": rep_cedula})
    chk("login portal con clave inicial (cédula)", rp.status_code == 200, rp.get_json())

    # ---------- PORTAL (registro propio + flujo) ----------
    p_cedula = "V-P" + _uid
    p_pass = "Smoke123"
    r = c.post("/api/portal/registro",
               json={"cedula": p_cedula, "password": p_pass, "nombres": "Smoke",
                     "apellidos": "Test", "email": "s2@x.com"})
    chk("portal registro", r.status_code == 201, r.get_json())

    rp = c.post("/api/portal/login", json={"usuario": p_cedula, "password": p_pass})
    chk("portal login", rp.status_code == 200, rp.get_json())
    ptok = (rp.get_json() or {}).get("token")
    chk("portal login devuelve JWT", bool(ptok))

    # Cliente SIN sesión, solo con Bearer (prueba JWT real)
    pc = app.test_client()
    auth = {"Authorization": f"Bearer {ptok}"}
    est_ced = "E-" + uuid.uuid4().hex[:8]
    r = pc.post("/api/portal/estudiantes",
                json={"cedula_escolar": est_ced, "nombres": "Alum", "apellidos": "Prueba",
                      "fecha_nacimiento": "2015-01-01"}, headers=auth)
    chk("portal crear estudiante (Bearer, sin sesión)", r.status_code == 201, r.get_json())

    r = pc.get("/api/portal/estudiantes", headers=auth)
    chk("portal listar estudiantes (Bearer, sin sesión)", r.status_code == 200)

    r = pc.post("/api/portal/inscripcion",
                json={"cedula_escolar": est_ced, "id_grado": 1}, headers=auth)
    chk("portal inscripcion (Bearer, sin sesión)", r.status_code == 201, r.get_json())

    r = pc.get(f"/api/portal/constancia/{est_ced}", headers=auth)
    chk("portal constancia PDF (Bearer, sin sesión)",
        r.status_code == 200 and r.content_type == "application/pdf",
        (r.status_code, r.content_type))

    r = pc.get("/api/portal/perfil", headers=auth)
    chk("portal perfil (Bearer, sin sesión)", r.status_code == 200)

    r = pc.put("/api/portal/password",
               json={"current": p_pass, "new_password": "Nueva123"}, headers=auth)
    chk("portal cambio password (Bearer, sin sesión)", r.status_code == 200, r.get_json())

    r = c.post("/api/portal/recuperar", json={"cedula": p_cedula})
    chk("portal recuperar", r.status_code == 200, r.get_json())

    r = c.post("/api/portal/logout")
    chk("portal logout", r.status_code == 200)

    # Limpiar BD temporal
    try:
        if os.path.exists(_TMP_DB):
            os.remove(_TMP_DB)
    except OSError:
        pass


if __name__ == "__main__":
    run()
    ok = sum(1 for _, v in results if v)
    fail = len(results) - ok
    print("\nRESUMEN: OK=%d FAIL=%d" % (ok, fail))
    sys.exit(1 if fail else 0)
