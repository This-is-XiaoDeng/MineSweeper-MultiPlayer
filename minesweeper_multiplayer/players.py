from typing import Any, Awaitable, Callable, Optional
from fastapi import WebSocket
import random

from .game_map import MineSweeperMap
from .session import Session, get_sessions

player_list: list["Player"] = []
FUNCTIONS = []

def requestable_function(func: Awaitable[Callable[..., None]]) -> Awaitable[Callable[..., None]]:
    FUNCTIONS.append(func.__name__)
    return func

class Player:

    def __init__(self, ws: WebSocket):
        self.session: Optional[Session] = None
        self.ready: bool = False
        self.game_map: Optional[MineSweeperMap] = None
        self.name = f"Player_{int(random.random() * 100000)}"
        self.ws = ws
        player_list.append(self)

    async def set_game_map(self, game_map: MineSweeperMap) -> None:
        self.game_map = game_map

    async def handle_request(self, data: dict[str, Any]) -> None:
        func = data.pop("func")
        if func in FUNCTIONS:
            return await getattr(self, func)(**data)
        await self.send_json(404, details="Function not found")

    @requestable_function
    async def get_game_map(self) -> None:
        if self.game_map is not None:
            await self.send_json(my_map=self.game_map.get_game_map(), other_map=[value for key, value in self.session.get_all_game_maps().items() if key != self.name][0])
        else:
            await self.send_json(403)

    @requestable_function
    async def mine_block(self, pos: list[int]) -> None:
        if await self.check_pos_form(pos):
            block = self.game_map.mine_block(pos)
            await self.handle_map_update(block)

    async def check_pos_form(self, pos: list[int]) -> bool:
        if self.game_map is None:
            await self.send_json(403)
        elif len(pos) != 2:
            await self.send_json(400, details="Pos 格式不正确")
        else:
            return True
        return False

    async def offline(self) -> None:
        if self.session is not None:
            await self.session.unset_session()
        player_list.remove(self)

    @requestable_function
    async def mark_block(self, pos: list[int]) -> None:
        if await self.check_pos_form(pos):
            self.game_map.mark_block(pos)
            await self.handle_map_update(-2)

    def unset_session(self) -> None:
        self.session = None
        self.ready = False
        self.game_map = None

    async def handle_map_update(self, block: int) -> None:
            game_map = self.game_map.get_game_map()
            await self.send_json(block=block, game_map=game_map)
            await self.session.notice_all_players("map.updated", name=self.name, game_map=game_map)
            await self.check_map_status()

    async def check_map_status(self) -> None:
        await self.session.update_map_status(self, self.game_map.check_status())

    async def send_json(self, code: int = 200, **kwargs) -> None:
        try:
            if 'subject' in kwargs:
                await self.ws.send_json(kwargs)
            else:
                await self.ws.send_json({"code": code, "data": kwargs})
        except RuntimeError:
            if kwargs.get('subject') != 'session.finished':
                await self.offline()

    def set_session(self, session: Session) -> None:
        self.session = session

    @requestable_function
    async def get_ready(self, ready: bool = True) -> None:
        if self.session is None:
            await self.send_json(403)
        self.ready = ready
        await self.session.player_get_ready(self, ready)


    @requestable_function
    async def set_name(self, name: str) -> None:
        for p in player_list:
            if p.name == name:
                await self.send_json(403, details="与现有玩家重名！")
                return
        self.name = str(name)
        await self.send_json()

    @requestable_function
    async def start_matching(self) -> None:
        if self.session is not None:
            await self.send_json(403, details="您已经在一个 Session 里面了")
        await self.send_json(200)
        for session in get_sessions().values():
            if session.is_matchable():
                await session.add_player(self)
                return
        self.set_session(Session())
        await self.session.add_player(self)



def get_player_count() -> int:
    return len(player_list)




