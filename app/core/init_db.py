import asyncio
from app.core.database import database
from app.models.schema import User, RecoveryData

async def init_db():
    user = await database["users"].find_one({"email": "test@vibe.com"})
    if not user:
        new_user = User(
            name="Elite Athlete",
            email="test@vibe.com",
            password="password123",
            strength_score=85.0,
            stamina_score=62.0,
            recovery_score=34.0,
            equipment_preference="gym",
            targeted_muscle_groups=[],
            mobility_test_results={}
        )
        user_result = await database["users"].insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
        user_id = str(user_result.inserted_id)
        
        # Add a default recovery entry representing low recovery
        recovery = RecoveryData(
            user_id=user_id,
            sleep_hours=4.5,
            soreness_level="High",
            cns_readiness=34.0
        )
        await database["recovery_data"].insert_one(recovery.model_dump(by_alias=True, exclude={"id"}))
        print("Database initialized successfully.")
    else:
        print("User test@vibe.com already exists. No initialization needed.")
    
if __name__ == "__main__":
    asyncio.run(init_db())
