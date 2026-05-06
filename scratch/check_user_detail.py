import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_users():
    load_dotenv()
    mongo_url = os.environ.get("MONGODB_URL")
    client = AsyncIOMotorClient(mongo_url)
    db = client.fitness_app
    
    user = await db["users"].find_one({"email": "ameerhamza031946@gamil.com"})
    if user:
        print(f"User found: {user}")
    else:
        print("User not found")
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
