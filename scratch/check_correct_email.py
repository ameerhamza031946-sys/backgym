import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_users():
    load_dotenv()
    mongo_url = os.environ.get("MONGODB_URL")
    client = AsyncIOMotorClient(mongo_url)
    db = client.fitness_app
    
    user = await db["users"].find_one({"email": "ameerhamza031946@gmail.com"})
    if user:
        print(f"User found: {user}")
    else:
        print("User NOT found with correct spelling")
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
