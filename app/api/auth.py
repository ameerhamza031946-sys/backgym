from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timedelta
from app.core.database import get_db
from app.models import schema, api_schemas
from app.core import security
from app.api import deps
from bson import ObjectId

router = APIRouter()

@router.post("/register")
async def register(request: api_schemas.RegisterRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    email = request.email.lower().strip()
    # Check if email exists
    existing_user = await db["users"].find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = security.get_password_hash(request.password)
    new_user = schema.User(
        name=request.name.strip(),
        email=email,
        password=hashed_password,
        onboarding_completed=False
    )
    result = await db["users"].insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
    return {"id": str(result.inserted_id), "name": new_user.name, "email": new_user.email}

@router.post("/login")
async def login(request: api_schemas.LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    email = request.email.lower().strip()
    user_dict = await db["users"].find_one({"email": email})
    
    user = schema.User(**user_dict) if user_dict else None
    
    # Check simple string equivalence for legacy users before hash checks
    if user and user.password == request.password:
        # User is using plain-text, hash it for the future
        hashed = security.get_password_hash(request.password)
        await db["users"].update_one(
            {"_id": ObjectId(user.id)},
            {"$set": {"password": hashed}}
        )
    elif not user or not security.verify_password(request.password, user.password):
        print(f"DEBUG: Failed login attempt for {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    print(f"DEBUG: Login successful for {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id, 
            "name": user.name, 
            "email": user.email, 
            "onboarding_completed": user.onboarding_completed
        }
    }
