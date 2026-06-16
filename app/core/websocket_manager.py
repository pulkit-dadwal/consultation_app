from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections = {}

    async def connect(
        self,
        user_id: str,
        websocket: WebSocket
    ):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(
            websocket
        )

    def disconnect(
        self,
        user_id: str,
        websocket: WebSocket
    ):
        if user_id not in self.active_connections:
            return

        if websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(
                websocket
            )

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_to_user(
        self,
        user_id: str,
        message: dict
    ):
        connections = self.active_connections.get(
            user_id,
            []
        )

        for websocket in connections:
            await websocket.send_json(
                message
            )

    async def broadcast(
        self,
        message: dict
    ):
        for connections in self.active_connections.values():

            for websocket in connections:

                await websocket.send_json(
                    message
                )


manager = ConnectionManager()