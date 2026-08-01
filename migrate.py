from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN estado VARCHAR(20) DEFAULT 'REGULAR';"))
        db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN fecha_retiro DATE;"))
        db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN lapso_registro VARCHAR(20) DEFAULT 'Lapso 1';"))
        db.session.execute(text("ALTER TABLE INSCRIPCION ADD COLUMN motivo_retiro TEXT;"))
        db.session.commit()
        print("Migracion exitosa")
    except Exception as e:
        print("Error:", e)
