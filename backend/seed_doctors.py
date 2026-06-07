import asyncio
import bcrypt
import motor.motor_asyncio
from database import MONGO_URI, DATABASE_NAME

async def seed_doctors():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    doctors = [
        {
            "name": "Dr. Ramesh",
            "email": "ramesh@hospital.com",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "role": "doctor"
        },
        {
            "name": "Dr. Smith",
            "email": "smith@hospital.com",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "role": "doctor"
        }
    ]
    
    for doc in doctors:
        existing = await db["USERS"].find_one({"email": doc["email"]})
        if not existing:
            await db["USERS"].insert_one(doc)
            print(f"Added {doc['name']}")
        else:
            print(f"{doc['name']} already exists")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_doctors())
