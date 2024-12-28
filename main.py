from fastapi import FastAPI, WebSocket
import os
from typing import Any
from players import Player, get_player_count
import uvicorn

app = FastAPI()
API_VERSION = 1


@app.get("/")
async def root() -> dict[str, Any]:
    return {"code": 200, "data": {"version": API_VERSION, "online": get_player_count()}}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    player = Player(ws)
    while True:
        recv = await ws.receive_json()
        if "func" in recv:
            await player.handle_request(recv)
        else:
            await ws.close(1400, "异常的数据包")
            break


if __name__ == "__main__":
    uvicorn.run(app, host=os.environ.get("SERVER_HOST", "0.0.0.0"), port=os.environ.get("PORT", 8080))
