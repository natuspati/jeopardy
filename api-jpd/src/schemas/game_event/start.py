from schemas.game import GameEventSchema, GamePayloadSchema


class GameStartedEvent(GameEventSchema):
    name: str = "game.started"
    payload: GamePayloadSchema
