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
#     Check each task route to ensure none return 404s
#     """
#
#     async def test_routes_exist(self, app: FastAPI, client: TestClient, test_task: TaskPublic) -> None:
#         res = await client.post(app.url_path_for("task:create-task"), json={})
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.get(app.url_path_for("task:get-task-by-id", task_id=test_task.id))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.get(app.url_path_for("task:get-all-tasks"))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.put(app.url_path_for("task:get-task-by-id", task_id=test_task.id))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
#         res = await client.delete(app.url_path_for("task:delete-task-by-id", task_id=test_task.id))
#         assert res.status_code != status.HTTP_404_NOT_FOUND
