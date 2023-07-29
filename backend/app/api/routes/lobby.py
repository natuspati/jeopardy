from typing import List

from fastapi import APIRouter, Body, Depends

from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.dependencies.database import get_repository

router = APIRouter()


@router.get(
    "/",
    response_description="List all lobbies",
    name="lobby:get-all"
)
async def list_all_lobbies(
):
    return {"text": "List all lobbies"}


@router.get(
    "/{lobby_id}/",
    response_description="Get lobby by id",
    name="lobby:get-by-id"
)
async def get_lobby_by_id(
    lobby_id: int
):
    return {"text": f"Get lobby by id: {lobby_id}"}


@router.post(
    "/",
    response_description="Create a new lobby",
    name="lobby:create"
)
async def create_new_lobby(
):
    return {"text": "Create new lobby"}


@router.put(
    "/{lobby_id}/",
    response_description="Update lobby by id",
    name="lobby:update-by-id"
)
async def update_lobby_by_id(
        lobby_id: int
):
    return {"text": f"Update lobby by id: {lobby_id}"}


@router.delete(
    "/{lobby_id}",
    response_description="Delete lobby by id",
    name="lobby:delete-by-id"
)
async def list_all_lobbies(
        lobby_id: int
):
    return {"text": f"Delete lobby by id: {lobby_id}"}
