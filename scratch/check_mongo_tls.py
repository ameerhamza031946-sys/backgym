import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    uri = os.environ.get("MONGODB_URL")
    # Adding tlsAllowInvalidCertificates=True for debugging
    if "?" in uri:
        uri += "&tlsAllowInvalidCertificates=true"
    else:
        uri += "?tlsAllowInvalidCertificates=true"
        
    print(f"Checking connection with tlsAllowInvalidCertificates=True to: {uri[:30]}...")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command('ping')
        print("Pinged your deployment successfully with invalid certs allowed!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
