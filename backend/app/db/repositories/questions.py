from typing import List
from bson import ObjectId

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.base import BaseRepository

from app.models.category import CategoryInDB
from app.models.question import QuestionPublic, QuestionInDB, QuestionCreate


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
            category_id: str,
    ) -> List[QuestionPublic]:
        question_records = await self.collection.find(
            {'category_id': category_id}
        ).to_list(1000)
        
        return [QuestionPublic.model_validate(q) for q in question_records]
    
    async def create_question(
            self,
            *,
            question: QuestionCreate,
            category_id: str,
            fetch=False
    ) -> QuestionInDB | None:
        """
        Create a new question.
        If fetch is False, do not fetch and return the new question from the database.
        """
        create_data = question.model_dump()
        create_data["category_id"] = category_id
        encoded_new_question = jsonable_encoder(create_data)
        inserted_new_question = await self.collection.insert_one(encoded_new_question)
        
        if fetch:
            fetched_new_question = await self.collection.find_one(
                {"_id": inserted_new_question.inserted_id}
            )
            return QuestionPublic.model_validate(fetched_new_question)
    
    async def delete_questions_for_category(
            self,
            *,
            category_id: str
    ):
        deleted_records = await self.collection.delete_many(
            {'category_id': category_id}
        )
        
        if not deleted_records.acknowledged:
            raise HTTPException(status_code=404, detail=f"Questions for category {category_id} not deleted")
        
        return deleted_records.deleted_count
