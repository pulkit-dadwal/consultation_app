import json

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
    Query
)

from app.core.websocket_manager import manager
from app.core.security import decode_access_token

router = APIRouter(
    tags=["websocket"]
)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # WebSocket connections cannot send Authorization headers, so the JWT
    # is passed as a query parameter: ws://host/ws?token=<jwt>
    # We decode and validate it before accepting the connection so
    # unauthenticated sockets are rejected immediately.
    try:
        payload = decode_access_token(token)
    except Exception:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user_id = payload.get("id")

    if not user_id:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # user_id from the token — not from the URL — so clients cannot
    # impersonate other users by changing the path parameter.
    user_id = str(user_id)

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except Exception:
                message = {"message": data}

            print(f"WebSocket message from {user_id}:", message)

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
        print(f"User {user_id} disconnected.")