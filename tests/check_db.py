
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the backend directory to sys.path to import app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.models.schema import User, Workout, RecoveryData, LoggedMeal
from app.core.database import SessionLocal

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Users found: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}")
        
    workouts = db.query(Workout).all()
    print(f"\nWorkouts found: {len(workouts)}")
    for w in workouts:
        print(f"ID: {w.id}, UserID: {w.user_id}, Title: {w.title}, Focus: {w.focus}, Completed: {w.completed}")
        
    recovery = db.query(RecoveryData).all()
    print(f"\nRecovery Data found: {len(recovery)}")
    
finally:
    db.close()
