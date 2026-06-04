import asyncio
from app.core.database import engine, Base
# We import the models so SQLAlchemy knows they exist before creating tables
from app.models.user import User
from app.models.api_key import ApiKey

async def verify_database():
    print("========== DATABASE DIAGNOSTIC ==========")
    print("[*] Attempting to connect to PostgreSQL...")
    
    try:
        # Open a connection to the database
        async with engine.begin() as conn:
            # Instruct SQLAlchemy to build the tables based on our Python models
            print("[*] Pushing table schemas to database...")
            await conn.run_sync(Base.metadata.create_all)
            
        print("[+] SUCCESS! Connection established and tables created cleanly.")
        print("=========================================\n")
    except Exception as e:
        print("[-] FAILED! Could not connect to the database.")
        print(f"Error Details: {e}")
        print("=========================================\n")

if __name__ == "__main__":
    asyncio.run(verify_database())