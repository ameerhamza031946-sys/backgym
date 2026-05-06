from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db
from app.core import security
from app.models import schema, api_schemas
from bson import ObjectId
from bson.errors import InvalidId

# We use the /api/auth/login endpoint for our token url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = api_schemas.TokenData(id=user_id)
        
        # Validate ObjectId format before querying
        try:
            target_id = ObjectId(token_data.id)
        except InvalidId:
            print(f"DEBUG: Invalid token ID format: {token_data.id}")
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user_data = await db["users"].find_one({"_id": target_id})
    if user_data is None:
        raise credentials_exception
        
    user_data["_id"] = str(user_data["_id"])
    return schema.User(**user_data)
