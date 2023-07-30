from typing import List
from bson import ObjectId

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.base import BaseRepository
from app.db.repositories.questions import QuestionRepository

from app.models.category import CategoryPublic, CategoryInDB, CategoryCreate, CategoryUpdate
from app.models.core import PyObjectId
from app.models.question import QuestionCreate


class CategoryRepository(BaseRepository):
    """"
    All database actions associated with the Category resource
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = self.db.get_collection("categories")
        self.question_repo = QuestionRepository(db)
    
    async def list_all_categories(
            self,
            *,
            populate=False
    ) -> List[CategoryInDB] | List[CategoryPublic]:
        """
        List all categories
        """
        category_records = await self.collection.find().to_list(1000)
        categories = [CategoryInDB(**c) for c in category_records]
        if populate:
            return [
                await self.populate_category(
                    category=category,
                )
                for category in categories
            ]
        return categories
    
    async def get_category_by_id(
            self,
            *,
            category_id: str | PyObjectId,
    ) -> CategoryInDB | None:
        fetched_category = await self.collection.find_one(
            {"_id": ObjectId(category_id) if isinstance(category_id, str) else category_id}
        )
        if fetched_category:
            return CategoryInDB(**fetched_category)
    
    async def create_category(
            self,
            *,
            category: CategoryCreate,
            question_repo: QuestionRepository
    ) -> CategoryPublic:
        """
        Create new category.
        If questions are not None, create questions for the category.
        """
        create_data = category.model_dump()
        new_questions = create_data.pop("questions")
        
        encoded_new_category = jsonable_encoder(create_data)
        inserted_new_category = await self.collection.insert_one(encoded_new_category)
        
        if not inserted_new_category.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on category {category.id} could not be acknowledged"
            )
        
        fetched_new_category = await self.get_category_by_id(category_id=inserted_new_category.inserted_id)
        
        if new_questions:
            [await question_repo.create_question(
                question=QuestionCreate.model_validate(question),
                category=fetched_new_category
            ) for question in new_questions]
        
        return await self.populate_category(category=fetched_new_category)
    
    async def update_category_by_id(
            self,
            *,
            category: CategoryInDB,
            category_update: CategoryUpdate
    
    ) -> CategoryInDB:
        """
        Update category.
        Only category name is allowed to change. Do not return list of questions associated with category.
        """
        update_data = category_update.model_dump(exclude_unset=True)
        
        # If no changes are submitted, raise 304 error
        if not update_data:
            raise HTTPException(status_code=304, detail=f"Category {category.id} is not modified")
        
        updated_category = category.model_copy(update=update_data)
        encoded_updated_category = jsonable_encoder(updated_category)
        
        inserted_category = await self.collection.update_one(
            {"_id": updated_category.id}, {"$set": encoded_updated_category}
        )
        
        if not inserted_category.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on category {category.id} could not be acknowledged"
            )
        
        if (
                fetched_updated_category := await self.get_category_by_id(category_id=updated_category.id)
        ) is None:
            raise HTTPException(status_code=404, detail=f"Category {category.id} not found")
        
        return fetched_updated_category
    
    async def delete_category_by_id(
            self,
            *,
            category: CategoryInDB
    ) -> None:
        """
        Delete category by its id. Removes related questions.
        """
        delete_result = await self.collection.delete_one({"_id": category.id})
        
        if delete_result.deleted_count != 1:
            raise HTTPException(status_code=404, detail=f"Category {category.id} not found")
        
        # Delete related questions to the category
        await self.question_repo.delete_questions_for_category(category_id=category.id)
    
    async def populate_category(
            self,
            *,
            category: CategoryInDB,
    ) -> CategoryPublic:
        """
        Populate Category with its questions
        """
        questions = await self.question_repo.list_questions_for_category(
            category_id=category.id
        )
        
        # Merge category information with queried questions
        dict_data = category.model_dump()
        dict_data["questions"] = [q.model_dump() for q in questions]
        
        return CategoryPublic.model_construct(**dict_data)
