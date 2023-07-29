from typing import List
from datetime import datetime

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.db.repositories.base import BaseRepository


# class TaskRepository(BaseRepository):
#     """"
#     All database actions associated with the Task resource
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.collection = self.db.get_collection("tasks")
#
#     async def list_all_tasks(self) -> List[TaskPublic]:
#         task_records = await self.collection.find().to_list(10)
#
#         return [TaskPublic.model_validate(t) for t in task_records]
#
#     async def create_task(self, *, task: TaskCreate) -> TaskPublic:
#         create_data = task.model_dump()
#         created_task = TaskInDB.model_validate(create_data)  # autofill created task with id and timestamp
#         encoded_created_task = jsonable_encoder(created_task)
#
#         new_task = await self.collection.insert_one(encoded_created_task)
#         fetched_created_task = await self.collection.find_one(
#             {"_id": new_task.inserted_id}
#         )
#
#         return TaskPublic.model_validate(fetched_created_task)
#
#     async def get_task_by_id(self, *, id: str, ) -> TaskPublic:
#         if (task := await self.collection.find_one({"_id": id})) is not None:
#             return TaskPublic.model_validate(task)
#
#     async def update_task_by_id(self, task_id: str, task: TaskPublic, task_update: TaskUpdate) -> TaskPublic:
#         update_data = task_update.model_dump(exclude_unset=True)
#
#         # if there are any changes, change updated field to now, else raise 304 error
#         if update_data:
#             update_data['updated'] = datetime.now()
#         else:
#             raise HTTPException(status_code=304, detail=f"Task {task_id} is not modified")
#
#         updated_task = task.model_copy(update=update_data)
#         encoded_updated_task = jsonable_encoder(updated_task)
#
#         await self.collection.update_one(
#             {"_id": task_id}, {"$set": encoded_updated_task}
#         )
#
#         if (
#                 fetched_updated_task := await self.collection.find_one({"_id": task_id})
#         ) is None:
#             raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
#
#         return TaskPublic.model_validate(fetched_updated_task)
#
#     async def delete_task_by_id(self, task_id: str):
#         delete_result = await self.collection.delete_one({"_id": task_id})
#
#         if delete_result.deleted_count != 1:
#             raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
#
#         return None