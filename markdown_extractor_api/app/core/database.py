from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 1. Create the async engine bridging FastAPI to PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False, # Set to True if you want to see raw SQL queries in your terminal
    future=True
)

# 2. Create a session factory to handle concurrent developer requests securely
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Base class that our User and API Key models will inherit from
Base = declarative_base()

# 4. FastAPI Dependency to inject the database session into our endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()