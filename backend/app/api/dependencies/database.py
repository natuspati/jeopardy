from typing import Callable, Type
from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi import Depends
from starlette.requests import Request

from app.db.repositories.base import BaseRepository


def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.database


def get_repository(Repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> Type[BaseRepository]:
        return Repo_type(db)
    
    return get_repo
