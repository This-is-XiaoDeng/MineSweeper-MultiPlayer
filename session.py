import asyncio
from fastapi import WebSocketDisconnect
import copy
import random
from typing import TYPE_CHECKING
import uuid
from game_map import generate_game_map, rotate_map, MineSweeperMap
from enum import Enum

if TYPE_CHECKING:
    from players import Player

sessions: dict[str, "Session"] = {}

class SessionStatus(Enum):
    joinable: int = 0
    preparing: int = 1
    playing: int = 2
    finished: int = 3

class Session:

    def __init__(self, matchable: bool = True) -> None:
        self.matchable = matchable
        self.status = SessionStatus.joinable
        self.players: list["Player"] = []
        self.id_ = uuid.uuid4().hex
        sessions[self.id_] = self

    def is_matchable(self) -> bool:
        return self.matchable and self.status == SessionStatus.joinable

    async def add_player(self, player: "Player") -> bool:
        if self.status != SessionStatus.joinable:
            return False
        if len(self.players) == 1:
            self.status = SessionStatus.preparing
        self.players.append(player)
        player.set_session(self)
        await self.notice_all_players("player.joined", name=player.name)
        await self.check_match_result()

    async def check_match_result(self) -> None:
        if self.status == SessionStatus.preparing and len(self.players) >= 2:
            await self.notice_all_players("session.matched", players=[p.name for p in self.players])
        else:
            self.status = SessionStatus.joinable

    async def update_map_status(self, player: "Player", check_result: None | bool) -> None:
        if check_result is None:
            return
        for p in self.players:
            p.game_map.lock()
        self.status = SessionStatus.finished
        if check_result:
            await self.notice_all_players("player.win", name=player.name)
        else:
            p_ = [p for p in self.players if p.name != player.name][0]
            await self.notice_all_players("player.win", name=p_.name)
        await self.unset_session()

    async def player_get_ready(self, player: "Player", ready: bool) -> None:
        await self.notice_all_players("player.ready", name=player.name, ready=ready)
        if all([p.ready for p in self.players]):
            asyncio.create_task(self.start_game())
    
    def get_all_game_maps(self) -> dict[str, list[list[int]]]:
            l = {}
            for p in self.players:
                l[p.name] = p.game_map.get_game_map()
            return l

    async def start_game(self) -> None:
        await self.send_map_to_player()
        self.status = SessionStatus.playing
        await self.send_counting(3)

    async def send_counting(self, start: int = 3) -> None:
        for i in range(start):
            await self.notice_all_players("counter.count", second=start-i)
            await asyncio.sleep(1)
        for p in self.players:
            p.game_map.unlock()
        await self.notice_all_players("counter.start")

    async def unset_session(self) -> None:
        await self.notice_all_players("session.finished")
        for p in self.players:
            p.unset_session() 
        sessions.pop(self.id_)

    async def send_map_to_player(self) -> None:
        origin_map = generate_game_map(9, 9, 9)
        for p in self.players:
            game_map = copy.deepcopy(origin_map)
            for _ in range(random.randint(0, 3)):
                game_map = rotate_map(game_map)
            await p.set_game_map(MineSweeperMap(game_map))

    async def notice_all_players(self, subject: str, **kwargs) -> None:
        for player in self.players:
            try:
                await player.send_json(0, subject=subject, **kwargs)
            except WebSocketDisconnect:
                if subject == "session.finished":
                    continue
                await self.unset_session()


def get_sessions() -> dict[str, "Session"]:
    return sessions
