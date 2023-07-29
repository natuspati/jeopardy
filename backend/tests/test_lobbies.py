# from datetime import datetime
# from typing import Dict, List, Optional, Callable
#
# import pytest
#
# from fastapi import FastAPI, status
# from async_asgi_testclient import TestClient
# from fastapi.encoders import jsonable_encoder
#
# pytestmark = pytest.mark.asyncio
#
#
# class TestTaskRoutes:
#     """
#     Check each lobby route to ensure none return 404s
#     """
#
#     async def test_routes_exist(self, app: FastAPI, client: TestClient) -> None:
#         res = await client.get(app.url_path_for("lobby:get-all"))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.get(app.url_path_for("lobby:get-by-id", lobby_id=1))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.post(app.url_path_for("lobby:create"), json={})
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.put(app.url_path_for("lobby:update-by-id", lobby_id=1))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.delete(app.url_path_for("lobby:delete-by-id", lobby_id=1))
#         assert res.status_code != status.HTTP_404_NOT_FOUND