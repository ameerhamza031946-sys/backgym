import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def fix_user_email():
    load_dotenv()
    mongo_url = os.environ.get("MONGODB_URL")
    client = AsyncIOMotorClient(mongo_url)
    db = client.fitness_app
    
    # Update ameerhamza031946@gamil.com to ameerhamza031946@gmail.com
    result = await db["users"].update_one(
        {"email": "ameerhamza031946@gamil.com"},
        {"$set": {"email": "ameerhamza031946@gmail.com"}}
    )
    
    if result.modified_count > 0:
        print("Successfully fixed email spelling to @gmail.com")
    else:
        print("Email was already correct or user not found.")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_user_email())
