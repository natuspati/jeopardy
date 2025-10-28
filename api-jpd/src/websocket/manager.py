from typing import Any

from websocket.server import sio


@sio.event
async def connect(sid: str, environ: Any) -> None:
    print(f"Socket.IO client connected: {sid}")


@sio.event
async def disconnect(sid: str) -> None:
    print(f"Socket.IO client disconnected: {sid}")
