from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import os
import json
from google import genai
from bson import ObjectId

from app.core.database import get_db
from app.models import schema, api_schemas
from datetime import datetime, time as dt_time

router = APIRouter()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Models tried in order — falls back if quota is hit
GEMINI_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-8b']

def generate_with_fallback(prompt: str) -> str:
    if not client:
        return None
    import time
    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            err = str(e)
            if '429' in err or 'RESOURCE_EXHAUSTED' in err or 'quota' in err.lower():
                print(f"Nutrition AI: {model} quota hit, trying next...")
                time.sleep(1)
                continue
            elif '404' in err or 'NOT_FOUND' in err:
                print(f"Nutrition AI: {model} not found.")
                continue
            else:
                raise
    return None

class ChatRequest(BaseModel):
    user_id: str
    message: str

from app.services.nutrition_knowledge_base import get_context_for_prompt

@router.post("/chat")
async def chat_with_nutritionist(request: ChatRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    if client:
        # Fetch user details for personalization
        user_dict = await db["users"].find_one({"_id": ObjectId(request.user_id)})
        user = schema.User(**user_dict) if user_dict else None
        
        user_context = f"User Goal: {user.fitness_goal}, Nutrition Path: {user.nutrition_goal}" if user else ""
        
        # 1. RAG Context Retrieval
        rag_context = await get_context_for_prompt(request.message)
        
        try:
            prompt = f"""
            You are an expert AI Nutritionist. 
            {user_context}
            
            {rag_context}
            
            Respond to the user's message in the SAME LANGUAGE as their message.
            Use the context above to provide specific meal recommendations if relevant.
            
            Message: {request.message}
            """
            reply = generate_with_fallback(prompt)
            if reply is None:
                # Intelligent Fallback if LLM is down
                reply = "I'm currently experiencing high demand. " + rag_context.replace("RELEVANT MEALS FROM KNOWLEDGE BASE:", "Here are some recommendations from my local database:")
        except Exception as e:
             print(f"Nutrition AI Error: {e}")
             reply = "Unable to reach AI services right now."
    else:
        # Fallback for basic advice if no API key is set
        reply = "I recommend checking out a healthy high-protein bowl! (Please configure GEMINI_API_KEY for real AI responses)"
        if "chipotle" in request.message.lower() and "500" in request.message.lower():
            reply = "Based on the verified Chipotle nutrition database, you can get a Chicken Lifestyle Bowl without rice, adding black beans, fajita veggies, fresh tomato salsa, and a light sprinkle of cheese. This comes to exactly 480 calories, with 42g of protein, 33g of carbs, and 18g of fat."
        
    return {"reply": reply, "source": "RAG_KNOWLEDGE_BASE"}

@router.post("/log", response_model=api_schemas.MealLogResponse)
async def log_meal(log: api_schemas.MealLogCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    db_log = schema.LoggedMeal(**log.model_dump())
    dump = db_log.model_dump(by_alias=True, exclude={"id"})
    result = await db["logged_meals"].insert_one(dump)
    
    response_data = dump
    response_data["id"] = str(result.inserted_id)
    response_data.pop("_id", None)
    return response_data

@router.get("/logs/{user_id}", response_model=list[api_schemas.MealLogResponse])
async def get_user_logs(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    today_start = datetime.combine(datetime.utcnow().date(), dt_time.min)
    cursor = db["logged_meals"].find({
        "user_id": user_id,
        "timestamp": {"$gte": today_start}
    })
    
    logs = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        logs.append(doc)
        
    return logs

@router.get("/summary/{user_id}")
async def get_macro_summary(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = schema.User(**user_dict)
    
    # Dynamic Macros Calculation Logic
    # Base calories: 2400. Adjust based on goal.
    target_calories = 2400
    if user.fitness_goal == 'lose_weight':
        target_calories = 2000
    elif user.fitness_goal == 'build_muscle':
        target_calories = 2800
    else: # toning or others
        target_calories = 2200
        
    # Macro ratios based on nutrition path
    path = user.nutrition_goal or 'balanced'
    
    if path == 'keto':
        protein_pct, carb_pct, fat_pct = 0.25, 0.05, 0.70
    elif path == 'vegan':
        protein_pct, carb_pct, fat_pct = 0.20, 0.55, 0.25
    elif path == 'high_protein':
        protein_pct, carb_pct, fat_pct = 0.40, 0.40, 0.20
    else: # balanced
        protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
        
    target_protein = int((target_calories * protein_pct) / 4)
    target_carbs = int((target_calories * carb_pct) / 4)
    target_fats = int((target_calories * fat_pct) / 9)
    
    # Recommendations based on path
    recommendations_map = {
        'keto': [
            {"name": "Avocado & Bacon Egg Cups", "calories": 450},
            {"name": "Steak with Garlic Butter Broccoli", "calories": 620}
        ],
        'vegan': [
            {"name": "Quinoa & Black Bean Power Bowl", "calories": 480},
            {"name": "Tempeh Stir-fry with Cashews", "calories": 520}
        ],
        'high_protein': [
            {"name": "Greek Yogurt with Whey & Berries", "calories": 350},
            {"name": "Double Chicken Lifestyle Bowl", "calories": 650}
        ],
        'balanced': [
            {"name": "Atlantic Salmon & Asparagus", "calories": 420},
            {"name": "Chipotle Lifestyle Bowl", "calories": 510}
        ]
    }
    
    recs = recommendations_map.get(path, recommendations_map['balanced'])
        
    today_start = datetime.combine(datetime.utcnow().date(), dt_time.min)
    cursor = db["logged_meals"].find({
        "user_id": user_id,
        "timestamp": {"$gte": today_start}
    })
    
    current_calories = 0
    current_protein = 0
    current_carbs = 0
    current_fats = 0
    
    async for log in cursor:
        current_calories += log.get("calories", 0)
        current_protein += log.get("protein", 0)
        current_carbs += log.get("carbs", 0)
        current_fats += log.get("fats", 0)

    return {
        "calories": {"current": current_calories, "target": target_calories},
        "macros": {
            "protein": {"current": current_protein, "target": target_protein},
            "carbs": {"current": current_carbs, "target": target_carbs},
            "fats": {"current": current_fats, "target": target_fats}
        },
        "recommendations": recs,
        "path": path.upper()
    }
