from collections.abc import AsyncIterator

from fastapi import WebSocket

from jlib.errors.resource import ResourceNotFoundError


class WSManager:
    def __init__(self, rooms: dict | None = None):
        self._rooms: dict[str | int, dict[str | int, WebSocket]] = rooms or {}

    async def add_connection(
        self,
        *,
        member_id: str | int,
        room_id: str | int,
        connection: WebSocket,
    ) -> None:
        await connection.accept()
        self._rooms.setdefault(room_id, {})[member_id] = connection

    async def remove_connection(
        self,
        *,
        member_id: str | int,
        room_id: str | int,
    ):
        try:
            connection = self._get_connection(member_id, room_id)
        except ResourceNotFoundError:
            pass
        else:
            await connection.close()
            del self._rooms[room_id][member_id]

    async def send_json(
        self,
        *member_ids: str | int,
        room_id: str | int,
        data: dict,
    ) -> None:
        connections = self._get_connections(*member_ids, room_id=room_id)
        for conn in connections:
            await conn.send_json(data)

    async def get_receiver(
        self,
        *,
        member_id: str | int,
        room_id: str | int,
    ) -> AsyncIterator[dict]:
        return self._get_connection(member_id, room_id).iter_json()

    def _get_room(self, room_id: str | int) -> dict[str | int, WebSocket]:
        try:
            room = self._rooms[room_id]
        except KeyError as error:
            raise ResourceNotFoundError(f"No connections found for room {room_id}") from error
        return room

    def _get_connection(self, member_id: str | int, room_id: str | int) -> WebSocket:
        room = self._get_room(room_id)
        try:
            return room[member_id]
        except KeyError as error:
            raise ResourceNotFoundError(f"No connection found for member {member_id}") from error

    def _get_connections(
        self,
        *member_ids: str | int,
        room_id: str | int,
    ) -> list[WebSocket]:
        room = self._get_room(room_id)
        if member_ids:
            return [room.get(mem) for mem in member_ids if room.get(mem)]
        return list(room.values())
