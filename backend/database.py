import os
from motor.motor_asyncio import AsyncIOMotorClient

# Default MongoDB URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lung_diagnosis"

client = None
db = None

async def connect_to_mongo():
    global client, db
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    print(f"Connected to db: {DATABASE_NAME}")

async def close_mongo_connection():
    global client
    print("Closing MongoDB connection...")
    if client:
        client.close()
        print("MongoDB connection closed.")

def get_database():
    return db
