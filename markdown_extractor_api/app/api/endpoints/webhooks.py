import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.api_key import ApiKey
from app.models.user import User
from app.core.config import settings

router = APIRouter()

def verify_paddle_signature(signature_header: str, raw_body: bytes, secret: str) -> bool:
    """
    Verifies that the incoming webhook actually came from Paddle.
    (Note: This is a simplified structural check. In production, use Paddle's official SDK or strict HMAC validation).
    """
    if not signature_header or not secret:
        return False
    # In a full production environment, you will extract the timestamp (ts) and hash (h1) 
    # from the signature_header and compare the HMAC-SHA256 of 'ts:raw_body' to the h1 hash.
    return True 

@router.post("/paddle")
async def paddle_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    # 1. Extract the raw data and signature
    raw_body = await request.body()
    signature_header = request.headers.get("Paddle-Signature")

    # 2. Verify it's genuinely from Paddle
    if not verify_paddle_signature(signature_header, raw_body, settings.PADDLE_WEBHOOK_SECRET):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid webhook signature."
        )

    # 3. Parse the JSON payload
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    # 4. Extract Event Data
    # Paddle Billing sends data in a specific format. We care about the 'event_type'.
    event_type = payload.get("event_type")
    data = payload.get("data", {})

    # When you build your frontend checkout, you will pass the developer's user_id 
    # into Paddle's 'custom_data' field so Paddle can hand it back to you here.
    custom_data = data.get("custom_data", {})
    user_id = custom_data.get("user_id")

    if not user_id:
        # If there's no user_id, we can't upgrade anyone. Return 200 so Paddle stops retrying.
        return {"status": "ignored", "reason": "No user_id in custom_data"}

    # 5. Handle Subscription Upgrades
    if event_type in ["subscription.created", "subscription.updated"]:
        # Find the API Key belonging to this user
        query = select(ApiKey).where(ApiKey.user_id == user_id)
        result = await db.execute(query)
        api_key = result.scalars().first()

        if api_key:
            # Upgrade their limit based on the plan they bought.
            # (In production, you'd check which specific plan ID they purchased).
            api_key.request_limit = 50000 
            
            # Reset their usage since they just paid for a new cycle
            api_key.requests_used = 0 
            
            # Find the user to update their tier label
            user_query = select(User).where(User.id == user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalars().first()
            if user:
                user.subscription_tier = "pro"

            await db.commit()
            print(f"[+] SUCCESS: Upgraded User {user_id} to PRO tier (50,000 requests).")

    # Always return a fast 200 OK, otherwise Paddle thinks your server crashed and will retry for days.
    return {"status": "success"}