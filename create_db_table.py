"""
Script para crear la base de datos `test.db` de forma
100% consistente con los modelos de SQLAlchemy del sistema.

En lugar de definir las tablas "a mano" con SQL, este script
inicializa la app Flask, ejecuta `db.create_all()` y deja que
los modelos de `models.py` sean la fuente de verdad.

Ademas, se ejecuta toda la logica de inicializacion que ya
existe en `app.py` (migraciones, usuario admin, datos de prueba, etc.).
"""

import os
from config import Config
from app import create_app


def recreate_database():
    """
    Elimina el archivo SQLite actual (si existe) y vuelve a crear
    toda la estructura usando los modelos y la logica de `create_app()`.
    """
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"--- Base de datos anterior eliminada: {db_path} ---")

    app = create_app()
    with app.app_context():
        print("[OK] Base de datos recreada usando los modelos y migraciones actuales.")


if __name__ == "__main__":
    recreate_database()
