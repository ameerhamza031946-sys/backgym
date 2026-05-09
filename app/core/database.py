from motor.motor_asyncio import AsyncIOMotorClient
import os
import certifi

MONGO_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    tlsCAFile=certifi.where()
)
database = client.fitness_app

async def get_db():
    yield database
