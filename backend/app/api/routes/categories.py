from typing import List

from fastapi import APIRouter, Body, Depends, Security

from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.category import get_category_by_id_from_path

from app.db.repositories.categories import CategoryRepository
from app.db.repositories.questions import QuestionRepository
from app.models.category import CategoryPublic, CategoryInDB, CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=List[CategoryInDB],
    response_description="List all categories",
    name="category:get-all"
)
async def list_all_categories(
        category_repo: CategoryRepository = Depends(get_repository(CategoryRepository)),
) -> List[CategoryInDB]:
    return await category_repo.list_all_categories(populate=False)


@router.get(
    "/{category_id}/",
    response_model=CategoryPublic,
    response_description="Get category by id",
    name="category:get-by-id"
)
async def get_category_by_id(
        category: CategoryInDB = Depends(get_category_by_id_from_path),
        category_repo: CategoryRepository = Depends(get_repository(CategoryRepository)),
) -> CategoryPublic:
    return await category_repo.populate_category(category=category)


@router.post(
    "/",
    response_model=CategoryPublic,
    status_code=HTTP_201_CREATED,
    response_description="Create a new category",
    name="category:create",
    dependencies=[Security(get_current_active_user, scopes=["resources"])]
)
async def create_new_category(
        category: CategoryCreate = Body(),
        category_repo: CategoryRepository = Depends(get_repository(CategoryRepository)),
        question_repo: QuestionRepository = Depends(get_repository(QuestionRepository))
) -> CategoryPublic:
    return await category_repo.create_category(category=category, question_repo=question_repo)


@router.put(
    "/{category_id}/",
    response_model=CategoryInDB,
    response_description="Update category by id",
    name="category:update-by-id",
    dependencies=[Security(get_current_active_user, scopes=["resources"])]
)
async def update_category_by_id(
        category_update: CategoryUpdate = Body(),
        category: CategoryInDB = Depends(get_category_by_id_from_path),
        category_repo: CategoryRepository = Depends(get_repository(CategoryRepository)),
) -> CategoryInDB:
    return await category_repo.update_category_by_id(category=category, category_update=category_update)


@router.delete(
    "/{category_id}",
    status_code=HTTP_204_NO_CONTENT,
    response_description="Delete category by id",
    name="category:delete-by-id",
    dependencies=[Security(get_current_active_user, scopes=["resources"])]
)
async def delete_category_by_id(
        category: CategoryInDB = Depends(get_category_by_id_from_path),
        category_repo: CategoryRepository = Depends(get_repository(CategoryRepository)),
) -> None:
    return await category_repo.delete_category_by_id(category=category)
