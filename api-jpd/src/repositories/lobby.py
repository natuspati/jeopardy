from sqlalchemy import and_, delete, desc, insert, select, update
from sqlalchemy.orm import selectinload

from configs import settings
from enums.lobby import LobbyStateEnum
from models.category import CategoryModel
from models.lobby import LobbyModel
from models.lobby_category import LobbyCategoryModel
from repositories.mixins import RelationalRepoMixin
from schemas.lobby.base import LobbyCreateSchema, LobbySearchSchema
from schemas.lobby.nested import LobbySchema
from schemas.lobby_category.base import BaseLobbyCategorySchema
from utils.validation import validate_model


class LobbyRepo(RelationalRepoMixin):
    async def select(self, lobby_id: int) -> LobbySchema:
        stmt = (
            select(LobbyModel)
            .where(LobbyModel.id == lobby_id)
            .options(
                selectinload(LobbyModel.host),
                selectinload(LobbyModel.lobby_categories),
                selectinload(LobbyModel.categories).options(selectinload(CategoryModel.prompts)),
            )
        )
        lobby = await self.scalar(stmt)
        return validate_model(lobby, LobbySchema)

    async def filter(self, search: LobbySearchSchema) -> list[LobbySchema]:
        filters = []
        if search.host_id is not None:
            filters.append(LobbyModel.host_id == search.host_id)
        if search.states:
            filters.append(LobbyModel.state.in_(search.states))
        if search.created_at is not None:
            filters.append(LobbyModel.created_at >= search.created_at)

        stmt = select(LobbyModel).options(
            selectinload(LobbyModel.host),
            selectinload(LobbyModel.lobby_categories),
            selectinload(LobbyModel.categories).options(selectinload(CategoryModel.prompts)),
        )
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.order_by(desc(LobbyModel.created_at)).limit(settings.page_size)
        lobbies = await self.scalars(stmt)
        return validate_model(lobbies, LobbySchema)

    async def insert(self, lobby: LobbyCreateSchema) -> LobbySchema:
        stmt = (
            insert(LobbyModel)
            .values(lobby.model_dump(exclude={"category_ids"}))
            .returning(LobbyModel.id)
        )
        lobby_id = await self.scalar(stmt)
        await self.execute(
            insert(LobbyCategoryModel),
            [
                BaseLobbyCategorySchema(category_id=cid, lobby_id=lobby_id).model_dump()
                for cid in lobby.category_ids
            ],
        )
        return await self.select(lobby_id)

    async def update(self, lobby_id: int, state: LobbyStateEnum) -> LobbySchema:
        stmt = update(LobbyModel).where(LobbyModel.id == lobby_id).values(state=state)
        await self.scalar(stmt)
        return await self.select(lobby_id)

    async def delete(self, lobby_id: int) -> None:
        stmt = delete(LobbyModel).where(LobbyModel.id == lobby_id)
        await self.execute(stmt)
