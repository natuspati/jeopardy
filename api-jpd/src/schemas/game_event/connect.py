from schemas.game import GameEventSchema, GamePayloadSchema


class ConnectEventSchema(GameEventSchema):
    name: str = "game.connect"
    payload: GamePayloadSchema


class DisconnectEventSchema(GameEventSchema):
    name: str = "game.disconnect"
    payload: GamePayloadSchema
