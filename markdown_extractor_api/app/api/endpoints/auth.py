from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas.user import UserCreate, UserResponse
from app.schemas.api_key import ApiKeyGenerateResponse, ApiKeyCreate
# Added verify_password to your security imports
from app.core.security import get_password_hash, generate_api_key, verify_password
import uuid

router = APIRouter()

# 1. Pydantic model for the incoming login request
class UserLoginRequest(BaseModel):
    email: str
    password: str

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
        "key": raw_api_key,         # Ensures frontend JS can easily grab keyData.key
        "raw_api_key": raw_api_key, # Kept for your response_model compatibility
        "prefix": key_prefix,
        "warning": "Please copy this key immediately. For security reasons, you will not be able to see it again."
    }

@router.post("/login")
async def login_user(request: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. Find the user by email
    query = select(User).where(User.email == request.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found. Please sign up.")

    # 2. Verify the password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password.")

    # 3. Fetch ALL API keys for this user
    key_query = select(ApiKey).where(ApiKey.user_id == user.id)
    key_result = await db.execute(key_query)
    api_keys = key_result.scalars().all()

    # 4. Format the keys for the dashboard
    keys_data = [
        {
            "name": k.name, 
            # We return a masked key because the raw key is not stored in the DB!
            "key": f"{k.prefix}****************", 
            "requests_used": getattr(k, 'requests_used', 0), # Safely get usage
            "created_at": k.created_at.strftime("%Y-%m-%d") if getattr(k, 'created_at', None) else "Today"
        } 
        for k in api_keys
    ]

    return {
        "status": "success",
        "user_id": str(user.id),
        "api_keys": keys_data
    }