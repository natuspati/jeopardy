from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.base import BaseRepository
from app.models.category import CategoryInDB

from app.models.core import PyObjectId
from app.models.question import QuestionPublic, QuestionCreate, QuestionUpdate


class QuestionRepository(BaseRepository):
    """"
    All database actions associated with the Question resource
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = self.db.get_collection("questions")
    
    async def list_questions_for_category(
            self,
            *,
            category_id: str | PyObjectId,
    ) -> List[QuestionPublic]:
        question_records = await self.collection.find(
            {'category_id': category_id if isinstance(category_id, str) else str(category_id)}
        ).to_list(1000)
        
        return [QuestionPublic(**q) for q in question_records]
    
    async def get_question_by_id(
            self,
            *,
            category_id: str | PyObjectId,
            question_id: str | PyObjectId
    ) -> QuestionPublic | None:
        """
        Get question with its id and its category id.
        """
        fetched_question = await self.collection.find_one(
            {
                "_id": PyObjectId(question_id) if isinstance(question_id, str) else question_id,
                "category_id":  category_id if isinstance(category_id, str) else str(category_id)
            }
        )
        if fetched_question:
            return QuestionPublic(**fetched_question)
    
    async def create_question(
            self,
            *,
            question: QuestionCreate,
            category: CategoryInDB,
    ) -> QuestionPublic | None:
        """
        Create a new question.
        """
        create_data = question.model_dump()
        create_data["category_id"] = str(category.id)
        encoded_new_question = jsonable_encoder(create_data)
        inserted_new_question = await self.collection.insert_one(encoded_new_question)
        
        if not inserted_new_question.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on question {question.id} could not be acknowledged"
            )
        
        return await self.get_question_by_id(
            category_id=category.id,
            question_id=inserted_new_question.inserted_id,
        )
    
    async def update_question_by_id(
            self,
            *,
            question: QuestionPublic,
            question_update: QuestionUpdate
    ) -> QuestionPublic:
        """
        Update question with its id.
        """
        update_data = question_update.model_dump(exclude_unset=True, exclude_none=True)
        
        # If no changes are submitted, raise 304 error
        if not update_data:
            raise HTTPException(status_code=304, detail=f"Question {question.id} is not modified")
        
        updated_question = question.model_copy(update=update_data)
        encoded_updated_question = jsonable_encoder(updated_question)
        
        inserted_question = await self.collection.update_one(
            {"_id": updated_question.id}, {"$set": encoded_updated_question}
        )
        
        if not inserted_question.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on question {question.id} could not be acknowledged"
            )
        
        if (
                fetched_updated_question := await self.get_question_by_id(
                    category_id=question.category_id,
                    question_id=question.id
                )
        ) is None:
            raise HTTPException(status_code=404, detail=f"Question {question.id} not found")
        
        return fetched_updated_question
    
    async def delete_question_by_id(
            self,
            *,
            question: QuestionPublic
    ) -> None:
        """
        Delete question by its id.
        """
        delete_result = await self.collection.delete_one({"_id": question.id})
        
        if delete_result.deleted_count != 1:
            raise HTTPException(status_code=404, detail=f"Question {question.id} not found")
    
    async def delete_questions_for_category(
            self,
            *,
            category_id: str | PyObjectId
    ) -> int:
        """
        Delete questions related to a category.
        """
        deleted_records = await self.collection.delete_many(
            {'category_id': category_id if isinstance(category_id, str) else str(category_id)}
        )
        
        if not deleted_records.acknowledged:
            raise HTTPException(status_code=404, detail=f"Questions for category {category_id} not deleted")
        
        return deleted_records.deleted_count
