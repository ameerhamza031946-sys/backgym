from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import os
import json
from google import genai

from app.core.database import get_db
from app.models import schema, api_schemas
from bson import ObjectId

router = APIRouter()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@router.get("/metrics/{user_id}", response_model=api_schemas.PerformanceStats)
async def get_performance_metrics(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "strength": int(user_dict.get("strength_score", 0)),
        "stamina": int(user_dict.get("stamina_score", 0)),
        "recovery": int(user_dict.get("recovery_score", 0)),
        "weekly_progress": [
            {"title": "FITAI HEAVY SQUATS", "time": "Yesterday", "metric": "+1.2k Vol", "trend": "+12%"},
            {"title": "FITAI ENDURANCE RUN", "time": "2 days ago", "metric": "5.4 km", "trend": "+5%"}
        ]
    }

@router.get("/alerts/{user_id}", response_model=api_schemas.RecoveryAlertResponse)
async def get_recovery_alerts(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        return {"has_warning": False, "message": None}
        
    recovery_dict = await db["recovery_data"].find_one(
        {"user_id": user_id},
        sort=[("date", -1)]
    )
    
    recovery_score = user_dict.get("recovery_score", 100)
    
    if recovery_score < 40.0:
        # 1. Multi-factor Risk Context
        context = {
            "recovery_score": recovery_score,
            "strength_score": user_dict.get("strength_score", 0),
            "sleep_hours": recovery_dict.get("sleep_hours", "unknown") if recovery_dict else "unknown",
            "soreness": recovery_dict.get("soreness_level", "unknown") if recovery_dict else "unknown",
            "trend": "decreasing" if recovery_score < 50 else "stable"
        }
        
        msg = f"Your recovery is low today ({recovery_score:.1f}%). Biometrics suggest reduced CNS readiness. Reduce intensity by 20% to avoid overtraining."
        
        if client:
             try:
                 prompt = f"""
                 Analyze the following biometric data for an athlete:
                 {json.dumps(context)}
                 
                 Identify specific risks (e.g. Overtraining, CNS Fatigue, Sleep Deprivation).
                 Provide a 2-sentence warning that is professional, empathetic, and scientifically grounded.
                 Advise on specific training adjustments (e.g. deload, active recovery, or complete rest).
                 """
                 response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                 msg = response.text.strip()
             except Exception as e:
                 print(f"Risk AI Error: {e}")
                 pass
        return {"has_warning": True, "message": msg}
        
    return {"has_warning": False, "message": None}
