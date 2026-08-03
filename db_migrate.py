# db_migrate.py - Migraciones ligeras que se ejecutan al arrancar cada app
from sqlalchemy import inspect, text


def migrar_bd():
    from models import db

    try:
        db.create_all()
    except Exception as e:
        print(f"[MIGRACION] create_all fallo: {e}")

    try:
        insp = inspect(db.engine)
        if 'USUARIO' in insp.get_table_names():
            columnas = {c['name'] for c in insp.get_columns('USUARIO')}
            if 'email' not in columnas:
                preparer = db.engine.dialect.identifier_preparer
                tabla = preparer.quote('USUARIO')
                db.session.execute(text(f"ALTER TABLE {tabla} ADD COLUMN email VARCHAR(100)"))
                db.session.commit()
                print("[MIGRACION] Columna USUARIO.email agregada")
    except Exception as e:
        db.session.rollback()
        print(f"[MIGRACION] Error al agregar USUARIO.email: {e}")
