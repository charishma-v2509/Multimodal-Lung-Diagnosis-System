import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_mongo():
    uri = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(uri)
    try:
        await client.admin.command('ismaster')
        print("--- MongoDB Status ---")
        print("Connection: SUCCESS")
        
        dbs = await client.list_database_names()
        print(f"Databases: {dbs}")
        
        if 'lung_diagnosis' in dbs:
            db = client['lung_diagnosis']
            collections = await db.list_collection_names()
            print(f"Collections: {collections}")
            
            for coll_name in collections:
                count = await db[coll_name].count_documents({})
                print(f"  - {coll_name}: {count} documents")
                if coll_name == 'USERS':
                    users = await db[coll_name].find().to_list(10)
                    print(f"    Sample Users: {[u.get('email') for u in users]}")
        else:
            print("Database 'lung_diagnosis' NOT found.")
            
    except Exception as e:
        print(f"Connection: FAILED - {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_mongo())
