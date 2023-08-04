import warnings
import os
import time
import binascii
from typing import List, Callable
from random import choice
from string import ascii_uppercase

import pytest
import pytest_asyncio
from fastapi import FastAPI
from async_asgi_testclient import TestClient
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import DATABASE_URL, DATABASE_NAME, JWT_TOKEN_PREFIX, SECRET_KEY

from app.db.repositories.categories import CategoryRepository
from app.db.repositories.questions import QuestionRepository
from app.db.repositories.users import UserRepository

from app.models.category import CategoryCreate, CategoryPublic
from app.models.question import QuestionCreate
from app.models.user import UserCreate, UserInDB

from app.services import auth_service


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
def app(prepare_test_env: Callable) -> FastAPI:
    from app.api.server import get_application
    return get_application()


@pytest_asyncio.fixture
def db(app: FastAPI) -> AsyncIOMotorDatabase:
    return app.database


@pytest_asyncio.fixture
async def client(app: FastAPI) -> TestClient:
    async with TestClient(app, headers={"Content-Type": "application/json"}) as client:
        yield client


@pytest.fixture
def authorized_client(client: TestClient, test_user: UserInDB) -> TestClient:
    access_token = auth_service.create_access_token_for_user(
        user=test_user, secret_key=str(SECRET_KEY)
    )
    
    client.headers = {
        **client.headers,
        "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}",
    }
    
    return client


@pytest.fixture
def admin_client(client: TestClient, admin_user: UserInDB) -> TestClient:
    access_token = auth_service.create_access_token_for_user(
        user=admin_user, secret_key=str(SECRET_KEY)
    )
    
    client.headers = {
        **client.headers,
        "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}",
    }
    
    return client


async def user_fixture_helper(
        *,
        db: AsyncIOMotorDatabase,
        new_user_instance: UserCreate,
        make_admin: bool = False
) -> UserInDB:
    user_repo = UserRepository(db)
    
    existing_user = await user_repo.get_user_by_email(email=new_user_instance.email)
    if existing_user:
        return existing_user
    
    registered_user = await user_repo.register_new_user(new_user=new_user_instance)
    if make_admin:
        return await user_repo.update_user_admin_status(user=registered_user, admin_status=True)
    
    return registered_user


@pytest_asyncio.fixture
def new_user_instance() -> UserCreate:
    random_string = ''.join(choice(ascii_uppercase) for i in range(12))
    return UserCreate(
        email=f"user_{random_string}@mail.io",
        username=f"user_{random_string}",
        password=f"{random_string}"
    )


@pytest_asyncio.fixture
def test_user_instance() -> UserCreate:
    return UserCreate(
        email=f"test_user@mail.io",
        username=f"test_user",
        password=f"testpassword"
    )


@pytest_asyncio.fixture
async def test_user(
        db: AsyncIOMotorDatabase,
        test_user_instance: UserCreate,
) -> UserInDB:
    return await user_fixture_helper(db=db, new_user_instance=test_user_instance)


@pytest_asyncio.fixture
async def admin_user(
        db: AsyncIOMotorDatabase,
) -> UserInDB:
    admin_user_create = UserCreate(
        email=f"admin_user@mail.io",
        username=f"admin_user",
        password=f"testpassword"
    )
    admin_user_in_db = await user_fixture_helper(db=db, new_user_instance=admin_user_create, make_admin=True)
    return admin_user_in_db


@pytest_asyncio.fixture
def new_empty_category_instance() -> CategoryCreate:
    return CategoryCreate(
        name="Test empty category",
    )


@pytest_asyncio.fixture
def new_populated_category_instance(question_factory: Callable) -> CategoryCreate:
    return CategoryCreate(
        name="Test populated category",
        questions=[
            question_factory(i) for i in range(3)
        ]
    )


@pytest_asyncio.fixture
async def empty_category(
        db: AsyncIOMotorDatabase,
        new_empty_category_instance: CategoryCreate,
) -> CategoryPublic:
    category_repo = CategoryRepository(db)
    question_repo = QuestionRepository(db)
    return await category_repo.create_category(
        category=new_empty_category_instance,
        question_repo=question_repo
    )


@pytest_asyncio.fixture
async def category_with_one_question(
        db: AsyncIOMotorDatabase,
        question_factory: Callable,
) -> CategoryPublic:
    category_repo = CategoryRepository(db)
    question_repo = QuestionRepository(db)
    populated_category = CategoryCreate(
        name="Test category with one question",
        questions=[question_factory(0)]
    )
    return await category_repo.create_category(
        category=populated_category,
        question_repo=question_repo
    )


@pytest_asyncio.fixture
async def category_with_three_questions(
        db: AsyncIOMotorDatabase,
        new_populated_category_instance: CategoryCreate
) -> CategoryPublic:
    category_repo = CategoryRepository(db)
    question_repo = QuestionRepository(db)
    return await category_repo.create_category(
        category=new_populated_category_instance,
        question_repo=question_repo
    )


@pytest_asyncio.fixture
async def category_list(
        empty_category: CategoryPublic,
        category_with_one_question: CategoryPublic
) -> List[CategoryPublic]:
    return [empty_category, category_with_one_question]


@pytest_asyncio.fixture
def question_factory() -> Callable:
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
