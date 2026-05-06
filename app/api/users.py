from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db
from app.models import schema, api_schemas
from app.api import deps
from app.core import security
from bson import ObjectId

router = APIRouter()

@router.get("/me", response_model=api_schemas.UserProfileUpdate)
async def read_user_me(current_user: schema.User = Depends(deps.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=api_schemas.UserProfileUpdate)
async def get_user_profile(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    if current_user.id != user_id and current_user.email != "admin@fitai.com": # basic role check
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict["_id"] = str(user_dict["_id"])
    return schema.User(**user_dict)

@router.put("/{user_id}", response_model=api_schemas.UserProfileUpdate)
async def update_user_profile(user_id: str, profile: api_schemas.UserProfileUpdate, db: AsyncIOMotorDatabase = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    
    user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = profile.model_dump(exclude_unset=True)
    if update_data:
        await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
    updated_user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    updated_user_dict["_id"] = str(updated_user_dict["_id"])
    return schema.User(**updated_user_dict)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    if current_user.id != user_id and current_user.email != "admin@fitai.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return None

@router.get("/", response_model=list[api_schemas.UserResponse])
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    # Restrict fetching all users to an admin or return subset in production
    if current_user.email != "admin@fitai.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list all users")
    
    cursor = db["users"].find().skip(skip).limit(limit)
    users = []
    async for user_dict in cursor:
        user_dict["id"] = str(user_dict["_id"])
        user_dict.pop("_id", None)
        users.append(user_dict)
        
    return users
