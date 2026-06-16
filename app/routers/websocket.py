import json

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from app.core.websocket_manager import (
    manager
)

router = APIRouter(
    tags=["websocket"]
)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str
):
    await manager.connect(
        user_id,
        websocket
    )

    try:

        while True:

            data = await websocket.receive_text()

            try:
                payload = json.loads(data)

            except Exception:
                payload = {
                    "message": data
                }

            print(
                f"WebSocket message from {user_id}:",
                payload
            )

    except WebSocketDisconnect:

        manager.disconnect(
            user_id,
            websocket
        )

        print(
            f"User {user_id} disconnected."
        )