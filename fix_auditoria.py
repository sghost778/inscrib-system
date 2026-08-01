"""fix_auditoria.py
Recrea la tabla REGISTRO_AUDITORIA con INTEGER PRIMARY KEY AUTOINCREMENT.
Ejecutar UNA sola vez cuando el servidor NO esté corriendo.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Ver esquema actual
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='REGISTRO_AUDITORIA'")
row = cur.fetchone()
print("Esquema actual:", row)

# SQLite no permite ALTER COLUMN, hay que recrear la tabla
# 1. Renombrar la tabla vieja
try:
    cur.execute("ALTER TABLE REGISTRO_AUDITORIA RENAME TO REGISTRO_AUDITORIA_old")
    print("Tabla renombrada a REGISTRO_AUDITORIA_old")
except Exception as e:
    print(f"Nota al renombrar: {e}")

# 2. Crear tabla nueva con INTEGER (autoincrement garantizado)
cur.execute("""
CREATE TABLE IF NOT EXISTS REGISTRO_AUDITORIA (
    id_log    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    accion    TEXT NOT NULL,
    detalle   TEXT,
    fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
)
""")
print("Tabla REGISTRO_AUDITORIA creada correctamente.")

# 3. Migrar datos si existían (ignorar si la tabla vieja no existía)
try:
    cur.execute("""
        INSERT INTO REGISTRO_AUDITORIA (id_usuario, accion, detalle, fecha_hora)
        SELECT id_usuario, accion, detalle, fecha_hora FROM REGISTRO_AUDITORIA_old
    """)
    print(f"Datos migrados: {cur.rowcount} filas.")
    cur.execute("DROP TABLE REGISTRO_AUDITORIA_old")
    print("Tabla vieja eliminada.")
except Exception as e:
    print(f"Nota en migración (puede ignorarse si era nueva): {e}")

conn.commit()
conn.close()
print("\n✅ Migración completada. Ahora puede iniciar el servidor.")
