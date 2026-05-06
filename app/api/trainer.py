from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import schema, api_schemas
from app.services.ai_trainer import generate_workout_plan
from bson import ObjectId

router = APIRouter()

@router.get("/workout/{workout_id}", response_model=api_schemas.WorkoutPlanResponse)
async def get_workout_by_id(workout_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    workout_dict = await db["workouts"].find_one({"_id": ObjectId(workout_id)})
    if not workout_dict:
        raise HTTPException(status_code=404, detail="Workout not found")
    workout_dict["id"] = str(workout_dict.pop("_id"))
    return workout_dict

@router.get("/today/{user_id}", response_model=api_schemas.WorkoutPlanResponse)
async def get_todays_workout(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    user = schema.User(**user_dict)
        
    recovery_dict = await db["recovery_data"].find_one(
        {"user_id": user_id},
        sort=[("date", -1)]
    )
    recovery = schema.RecoveryData(**recovery_dict) if recovery_dict else None
    print(f"DEBUG: Recovery data: {recovery_dict}")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    workout_dict = await db["workouts"].find_one({
        "user_id": user_id, 
        "date": {"$gte": today_start}
    })
    
    if workout_dict:
        workout_dict["id"] = str(workout_dict.pop("_id"))
        return workout_dict
        
    user_profile = {
        "id": user.id,
        "name": user.name,
        "goal": user.fitness_goal,
        "level": user.fitness_level,
        "equipment_preference": user.equipment_preference,
        "targeted_muscle_groups": user.targeted_muscle_groups or [],
        "mobility_test_results": user.mobility_test_results or {},
        "training_frequency": user.training_frequency,
        "strength": user.strength_score,
        "stamina": user.stamina_score
    }
    recovery_metrics = {"sleep_hours": recovery.sleep_hours, "cns_readiness": recovery.cns_readiness} if recovery else {}
    
    ai_plan = await generate_workout_plan(user_profile, recovery_metrics)
    
    new_workout = schema.Workout(
        user_id=user.id,
        title="Daily Session",
        focus=ai_plan.get("focus", "General"),
        duration_mins=ai_plan.get("duration_mins", 45),
        calories=ai_plan.get("calories", 350),
        exercises=ai_plan.get("exercises", []),
        completed=False,
        date=datetime.utcnow()
    )
    
    workout_dump = new_workout.model_dump(by_alias=True, exclude={"id"})
    result = await db["workouts"].insert_one(workout_dump)
    
    workout_response = workout_dump
    workout_response["id"] = str(result.inserted_id)
    workout_response.pop("_id", None)
    return workout_response

@router.post("/complete", response_model=api_schemas.WorkoutPlanResponse)
async def complete_workout(request: api_schemas.CompleteWorkoutRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    workout_dict = await db["workouts"].find_one({"_id": ObjectId(request.workout_id)})
    if not workout_dict:
        raise HTTPException(status_code=404, detail="Workout not found")
        
    await db["workouts"].update_one(
        {"_id": ObjectId(request.workout_id)},
        {"$set": {"completed": True}}
    )
    
    # Update user metrics
    user_id = workout_dict["user_id"]
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user_dict:
        strength_score = min(100.0, user_dict.get("strength_score", 0) + 0.5)
        stamina_score = min(100.0, user_dict.get("stamina_score", 0) + 1.2)
        recovery_score = max(0.0, user_dict.get("recovery_score", 0) - 15.0)
        
        await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "strength_score": strength_score,
                "stamina_score": stamina_score,
                "recovery_score": recovery_score
            }}
        )
        
    updated_workout = await db["workouts"].find_one({"_id": ObjectId(request.workout_id)})
    updated_workout["id"] = str(updated_workout.pop("_id"))
    return updated_workout
