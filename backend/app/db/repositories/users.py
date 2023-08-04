from typing import Optional

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING
from pydantic import EmailStr
from starlette import status

from app.db.repositories.base import BaseRepository

from app.models.core import PyObjectId
from app.models.user import UserInDB, UserCreate

from app.services import auth_service

COLLECTION_CONFIG = {
    "name": "users",
    "index_fields": [
        ("email", ASCENDING),
        ("username", ASCENDING)
    ]
}


class UserRepository(BaseRepository):
    """"
    All database actions associated with the Category resource
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = self.db.get_collection(COLLECTION_CONFIG["name"])
        self.auth_service = auth_service
    
    async def get_user_by_id(
            self,
            *,
            user_id: str | PyObjectId
    ) -> Optional[UserInDB]:
        user_record = await self.collection.find_one(
            {"_id": PyObjectId(user_id) if isinstance(user_id, str) else user_id}
        )
        if user_record:
            return UserInDB(**user_record)
    
    async def get_user_by_email(
            self,
            *,
            email: EmailStr
    ) -> Optional[UserInDB]:
        user_record = await self.collection.find_one(
            {"email": email}
        )
        if user_record:
            return UserInDB(**user_record)
    
    async def get_user_by_username(
            self,
            *,
            username: str
    ) -> Optional[UserInDB]:
        user_record = await self.collection.find_one(
            {"username": username}
        )
        if user_record:
            return UserInDB(**user_record)
    
    async def register_new_user(
            self,
            *,
            new_user: UserCreate
    ) -> UserInDB:
        if await self.get_user_by_email(email=new_user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is already taken. Login with that email or register with another one.",
            )
        
        if await self.get_user_by_username(username=new_user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That username is already taken. Please try another one.",
            )
        
        user_password_update = self.auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
        new_user_params = new_user.model_dump() | user_password_update.model_dump()
        encoded_new_user_params = jsonable_encoder(new_user_params)
        created_user = await self.collection.insert_one(encoded_new_user_params)
        
        fetched_user = await self.get_user_by_id(user_id=created_user.inserted_id)
        return fetched_user
    
    async def authenticate_user(
            self,
            *,
            email: EmailStr,
            password: str
    ) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email=email)
        
        if not user:
            return None
        
        if not self.auth_service.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            return None
        
        return user
