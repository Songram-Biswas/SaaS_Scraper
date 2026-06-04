from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas.user import UserCreate, UserResponse
from app.schemas.api_key import ApiKeyGenerateResponse, ApiKeyCreate
from app.core.security import get_password_hash, generate_api_key
import uuid

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if the email already exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A developer with this email is already registered."
        )
        
    # 2. Hash the password and save the new user
    hashed_password = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.post("/users/{user_id}/generate-key", response_model=ApiKeyGenerateResponse)
async def create_api_key(user_id: uuid.UUID, key_in: ApiKeyCreate, db: AsyncSession = Depends(get_db)):
    # 1. Verify the user exists
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    # 2. Generate the secure cryptographic key
    raw_api_key, key_prefix, hashed_key = generate_api_key()
    
    # 3. Store ONLY the hash and the prefix in the database
    new_api_key = ApiKey(
        key_hash=hashed_key,
        prefix=key_prefix,
        name=key_in.name,
        user_id=user.id,
        request_limit=1000 # Default free tier limit
    )
    
    db.add(new_api_key)
    await db.commit()
    
    # 4. Return the raw key to the user exactly ONCE
    return {
        "message": f"API Key '{key_in.name}' generated successfully.",
        "raw_api_key": raw_api_key,
        "prefix": key_prefix,
        "warning": "Please copy this key immediately. For security reasons, you will not be able to see it again."
    }