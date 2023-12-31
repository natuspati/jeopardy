from typing import Any, Optional, Annotated
from datetime import datetime
from bson import ObjectId

from pydantic import (
    BaseModel, Field, field_serializer, ConfigDict, GetCoreSchemaHandler, field_validator, GetJsonSchemaHandler
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(ObjectId))
    
    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())



class CoreModel(BaseModel):
    """
    Any common logic to be shared by all models goes here
    """
    
    pass


class IDModelMixin(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(
        default_factory=PyObjectId,
        validation_alias="_id",
        alias="id"
    )
    
    @field_serializer('id')
    def serialize_id(self, object_id: PyObjectId, _info):
        return str(object_id)


class UpdatedAtModelMixin(BaseModel):
    updated_at: Optional[datetime] = datetime.now()
    
    @field_validator("updated_at", mode="before")  # noqa
    @classmethod
    def default_datetime(cls, value: datetime) -> datetime:
        return value or datetime.now()
