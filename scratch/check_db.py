import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_users():
    load_dotenv()
    mongo_url = os.environ.get("MONGODB_URL")
    if not mongo_url:
        print("No MONGODB_URL found in .env")
        return

    client = AsyncIOMotorClient(mongo_url)
    db = client.fitness_app
    
    print(f"Connecting to: {mongo_url}")
    try:
        users = await db["users"].find().to_list(length=100)
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- Name: {user.get('name')}, Email: {user.get('email')}, Onboarding: {user.get('onboarding_completed')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
