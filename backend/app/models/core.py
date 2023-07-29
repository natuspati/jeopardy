import uuid
from typing import Any

from bson.objectid import ObjectId
from pydantic import BaseModel, Field, field_serializer, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    # @classmethod
    # def __get_pydantic_json_schema__(cls, field_schema):
    #     field_schema.update(type="string")
    
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(ObjectId))


class CoreModel(BaseModel):
    """
    Any common logic to be shared by all models goes here
    """
    
    pass


class IDModelMixin(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, validation_alias="_id")
    
    @field_serializer('id')
    def serialize_id(self, dt: PyObjectId, _info):
        return str(dt)

