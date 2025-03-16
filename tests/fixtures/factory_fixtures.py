from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from jlib.schemas.category import CategoryInGameSchema
from jlib.schemas.lobby import LobbySchema
from jlib.schemas.player import PlayerSchema


@register_fixture
class CategoryInGameFactory(ModelFactory[CategoryInGameSchema]):
    __model__ = CategoryInGameSchema


@register_fixture
class PlayerFactory(ModelFactory[PlayerSchema]):
    __model__ = PlayerSchema


@register_fixture
class LobbyFactory(ModelFactory[LobbySchema]):
    __model__ = LobbySchema
