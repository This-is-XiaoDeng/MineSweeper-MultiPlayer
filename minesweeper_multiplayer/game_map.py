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
            for x1, y1 in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y - 1), (x - 1, y + 1)]:
                if x1 < 0 or x1 >= width or y1 < 0 or y1 >= height:
                    continue
                if game_map[y1][x1] == 10:
                    c += 1
            game_map[y][x] = c
    return game_map


def rotate_map(origin_game_map: list[list[int]]) -> list[list[int]]:
    matrix = origin_game_map
    if not matrix or not matrix[0]:
        return []
    transposed_matrix = list(zip(*matrix))
    rotated_matrix = [list(row)[::-1] for row in transposed_matrix]
    return rotated_matrix


class MineSweeperMap:

    def __init__(self, game_map: list[list[int]]) -> None:
        self.game_map = game_map
        self.is_locked = True
        self.current_map = [[-1 for _ in range(len(self.game_map[0]))] for _ in range(len(self.game_map))]
        # -2: 标记  |  -1: 未挖开  |  0: 空  | 1~9: 数字  |  10： 雷

    def check_status(self) -> None | bool:
        for y in range(len(self.current_map)):
            for x in range(len(self.current_map[y])):
                if self.current_map[y][x] == 10:
                    return False
        if all([all(self.current_map[y][x] == self.game_map[y][x] for x in range(len(self.game_map[y])) if 0 <= self.game_map[y][x] <= 9) for y in range(len(self.game_map))]):
            return True



    def lock(self) -> None:
        self.is_locked = True


    def unlock(self) -> None:
        self.is_locked = False

    def get_game_map(self) -> list[list[int]]:
        return self.current_map

    def mark_block(self, pos: list[int]) -> None:
        if not self.lock:
            x, y = pos
            self.current_map[y][x] = -2

    def mine_block(self, pos: list[int], cont: bool = True) -> int:
        if self.is_locked:
            return -1
        x, y = pos
        if self.current_map[y][x] == -2:
            return -2
        self.current_map[y][x] = self.game_map[y][x]
        if self.game_map[y][x] != 0:
            return self.current_map[y][x]
        for x1, y1 in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if x1 < 0 or x1 >= len(self.game_map[0]) or y1 < 0 or y1 >= len(self.game_map):
                continue
            if 0 <= self.game_map[y1][x1] <= 9 and self.current_map[y1][x1] == -1 and cont:
                self.mine_block([x1, y1], self.game_map[y1][x1] == 0)
        return self.current_map[y][x]

