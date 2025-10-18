from pydantic import BaseModel


class BaseLobbyCategorySchema(BaseModel):
    lobby_id: int
    category_id: int
