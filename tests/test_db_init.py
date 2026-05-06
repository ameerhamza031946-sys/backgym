
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.init_db import init_db
from app.core.database import engine

print("Starting DB initialization...")
try:
    init_db()
    print("DB initialization successful!")
except Exception as e:
    print(f"DB initialization failed: {e}")
