import warnings
import os
import time
import binascii
from typing import List, Callable

import pytest
import pytest_asyncio
from fastapi import FastAPI
from async_asgi_testclient import TestClient
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import DATABASE_URL, DATABASE_NAME
from app.db.repositories.categories import CategoryRepository
from app.db.repositories.questions import QuestionRepository
from app.models.category import CategoryCreate, CategoryPublic
from app.models.question import QuestionCreate


@pytest.fixture(scope="session")
def prepare_test_env() -> None:
    # Create synchronous Mongodb and set testing to True
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    mongo_client = MongoClient(DATABASE_URL)
    initial_database_count = len(mongo_client.list_database_names())
    
    yield None
    
    # Drop test database
    mongo_client.drop_database(f"{DATABASE_NAME}_test")
    final_database_count = len(mongo_client.list_database_names())
    assert initial_database_count == final_database_count


@pytest_asyncio.fixture
def app(prepare_test_env: None) -> FastAPI:
    from app.api.server import get_application
    return get_application()


@pytest_asyncio.fixture
def db(app: FastAPI) -> AsyncIOMotorDatabase:
    return app.database


@pytest_asyncio.fixture
async def client(app: FastAPI) -> TestClient:
    async with TestClient(app, headers={"Content-Type": "application/json"}) as client:
        yield client


@pytest_asyncio.fixture
def new_empty_category_dict() -> CategoryCreate:
    return CategoryCreate(
        name="Test empty category",
    )


@pytest_asyncio.fixture
def new_populated_category_dict(new_question_factory: Callable) -> CategoryCreate:
    return CategoryCreate(
        name="Test populated category",
        questions=[
            new_question_factory(i) for i in range(3)
        ]
    )


@pytest_asyncio.fixture
async def new_empty_category(db: AsyncIOMotorDatabase) -> CategoryPublic:
    category_repo = CategoryRepository(db)
    question_repo = QuestionRepository(db)
    
    empty_category = CategoryCreate(
        name="New empty category",
    )
    created_empty_category = await category_repo.create_category(
        category=empty_category,
        question_repo=question_repo
    )
    
    return created_empty_category


@pytest_asyncio.fixture
async def new_categories_list(
        db: AsyncIOMotorDatabase,
        new_empty_category_dict: CategoryCreate,
        new_populated_category_dict: CategoryCreate
) -> List[CategoryPublic]:
    category_repo = CategoryRepository(db)
    question_repo = QuestionRepository(db)
    
    # Create empty category
    empty_category = new_empty_category_dict
    created_empty_category = await category_repo.create_category(
        category=empty_category,
        question_repo=question_repo
    )
    
    # Create populated category
    populated_category = new_populated_category_dict
    created_populated_category = await category_repo.create_category(
        category=populated_category,
        question_repo=question_repo
    )
    
    return [created_empty_category, created_populated_category]


@pytest_asyncio.fixture
def new_question_factory() -> Callable:
    def _new_question(i: int) -> QuestionCreate:
        return QuestionCreate(
            question=f"Test question {i}",
            answer=f"Test answer {i}",
            value=i + 10
        )
    
    return _new_question


@pytest_asyncio.fixture
def random_object_id_str() -> str:
    """
    Generate a random Object ID string based on the current timestamp.
    """
    timestamp = int(time.time())
    rest = binascii.b2a_hex(os.urandom(8)).decode("ascii")
    return f"{timestamp:x}{rest}"
