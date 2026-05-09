from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
print(f"DEBUG: Connecting to MongoDB (length: {len(MONGO_URL)})")

client = AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    tlsAllowInvalidCertificates=True,
    tls=True,
    retryWrites=True
)
database = client.fitness_app

async def get_db():
    yield database
