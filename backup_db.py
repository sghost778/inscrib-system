import shutil, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')

os.makedirs(BACKUP_DIR, exist_ok=True)

if os.path.exists(DB_PATH):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'test_db_backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(DB_PATH, backup_path)
    print(f'[OK] Backup creado: {backup_name}')
else:
    print('[WARN] test.db no encontrado')
