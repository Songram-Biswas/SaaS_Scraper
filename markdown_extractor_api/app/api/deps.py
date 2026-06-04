import hashlib
from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.api_key import ApiKey

# This tells FastAPI to look for an "X-API-Key" header in incoming requests
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validate_api_key(
    api_key_header: str = Depends(API_KEY_HEADER),
    db: AsyncSession = Depends(get_db)
) -> ApiKey:
    
    # 1. Did they provide a key?
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing from X-API-Key header."
        )
    
    # 2. Hash the incoming key so we can compare it to the DB
    hashed_key = hashlib.sha256(api_key_header.encode()).hexdigest()
    
    # 3. Search the database for this hashed key
    query = select(ApiKey).where(ApiKey.key_hash == hashed_key)
    result = await db.execute(query)
    api_key_record = result.scalars().first()

    # 4. Check if the key exists and hasn't been disabled
    if not api_key_record or not api_key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key."
        )

    # 5. Check if they have exceeded their monthly quota
    if api_key_record.requests_used >= api_key_record.request_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API request limit exceeded for this billing cycle."
        )

    # 6. If everything passes, increment their usage count and save
    api_key_record.requests_used += 1
    await db.commit()
    
    return api_key_record