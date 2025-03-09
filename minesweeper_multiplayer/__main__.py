from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
from typing import Any
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from .players import Player, get_player_count

app = FastAPI()
API_VERSION = 1


# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

@app.get("/")
async def root() -> dict[str, Any]:
    return {"code": 200, "data": {"version": API_VERSION, "online": get_player_count()}}

async def handle_websocket_connect(ws: WebSocket, player: Player) -> None:
    while True:
        recv = await ws.receive_json()
        print(recv)
        if "func" in recv:
            await player.handle_request(recv)
        else:
            await ws.close(400, "异常的数据包")
            raise ValueError("数据包异常")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    player = Player(ws)
    try:
        await handle_websocket_connect(ws, player)
    except (ValueError, WebSocketDisconnect, RuntimeError) as e:
        await player.offline()
        raise e


if __name__ == "__main__":
    uvicorn.run(app, host=os.environ.get("SERVER_HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 8080)))
