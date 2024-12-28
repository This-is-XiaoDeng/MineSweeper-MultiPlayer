import random


def generate_game_map(width: int, height: int, count: int = 9) -> list[list[int]]:
    game_map = [[0 for _ in range(width)] for _ in range(height)]
    for _ in range(count):
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if game_map[y][x] == 0:
                game_map[y][x] = 10
                break
    for y in range(height):
        for x in range(width):
            if game_map[y][x] == 10:
                continue
            c = 0
            for x1, y1 in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if x1 < 0 or x1 >= width or y1 < 0 or y1 >= height:
                    continue
                if game_map[y1][x1] == 10:
                    c += 1
            game_map[y][x] = c
    return game_map


def rotate_map(origin_game_map: list[list[int]]) -> list[list[int]]:
    game_map = []
    for x in range(len(origin_game_map[0])):
        line = []
        for y in range(len(origin_game_map)):
            line.append(origin_game_map[len(origin_game_map) - y][x])
        game_map.append(line)
    return game_map


class MineSweeperMap:

    def __init__(self, game_map: list[list[int]]) -> None:
        self.game_map = game_map
        self.lock = True
        self.current_map = [[-1 for _ in range(len(self.game_map[0]))] for _ in range(len(self.game_map))]
        # -2: 标记  |  -1: 未挖开  |  0: 空  | 1~9: 数字  |  10： 雷

    def check_status(self) -> None | bool:
        for y in range(len(self.current_map)):
            for x in range(len(self.current_map[y])):
                if self.current_map[y][x] == 10:
                    return False
                elif 0 <= self.game_map[y][x] <= 9 and self.current_map[y][x] == self.game_map[y][x]:
                    return True

    def lock(self) -> None:
        self.lock = True


    def unlock(self) -> None:
        self.lock = False

    def get_game_map(self) -> list[list[int]]:
        return self.current_map

    def mark_block(self, pos: list[int]) -> None:
        if not self.lock:
            x, y = pos
            self.current_map[y][x] = -2

    def mine_block(self, pos: list[int]) -> int:
        if self.lock:
            return -1
        x, y = pos
        if self.current_map[y][x] == -2:
            return -2
        self.current_map[y][x] = self.game_map[y][x]
        for x1, y1 in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if x1 < 0 or x1 >= len(self.game_map[0]) or y1 < 0 or y1 >= len(self.game_map):
                continue
            if self.game_map[y1][x1] == 0:
                self.mine_block([x1, y1])
        return self.current_map[y][x]

