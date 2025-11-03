from pydantic import BaseModel

from schemas.game import GameEventSchema


class GameErrorPayloadSchema(BaseModel):
    detail: str


class GameErrorEvent(GameEventSchema):
    name: str = "game.error"
    payload: GameErrorPayloadSchema
