import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import certifi
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    uri = os.environ.get("MONGODB_URL")
    print(f"Checking connection with certifi to: {uri[:30]}...")
    client = AsyncIOMotorClient(
        uri, 
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where()
    )
    try:
        await client.admin.command('ping')
        print("Pinged your deployment successfully with certifi!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
