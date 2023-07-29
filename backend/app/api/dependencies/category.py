from fastapi import Path, Depends, HTTPException, Body
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from app.api.dependencies.database import get_repository
from app.db.repositories.categories import CategoryRepository
from app.models.category import CategoryPublic, CategoryUpdate, CategoryInDB


async def get_category_by_id_from_path(
        category_id: str = Path(...),
        category_repo: CategoryRepository = Depends(get_repository(CategoryRepository)),
) -> CategoryInDB:
    category = await category_repo.get_category_by_id(category_id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No category found with that id.",
        )
    
    return category
