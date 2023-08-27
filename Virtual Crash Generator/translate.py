from typing import Generator


class Translate:
    def __init__(self, init_pos: tuple[float, float, float], human_num: int) -> None:
        self.init_pos = init_pos
        self.human_num = human_num


class Square(Translate):
    def __init__(self, init_pos: tuple[float, float, float], human_num: int, interval: tuple[float, float, float] = (1, 1, 0)) -> None:
        super().__init__(init_pos, human_num)
        self.set_interval(interval)

    def set_interval(self, interval: tuple[float, float, float]) -> None:
        self.interval_x: float = interval[0]
        self.interval_y: float = interval[1]
        self.interval_z: float = interval[2]

    def trans(self, direction: str = 'rt') -> Generator:
        side = 1
        while side**2 < self.human_num:
            side += 1

        directions = {
            'rt', 'rb',
            'lt', 'lb',
            'tr', 'tl',
            'br', 'bl'
        }
        if direction not in directions:
            raise ValueError(f"direction must be one of {directions}.")

        way1, way2 = list(direction)
        ways = {
            'r': self.right,
            'l': self.left,
            't': self.top,
            'b': self.bottom
        }

        pos = list(self.init_pos)
        for i in range(1, self.human_num + 3):
            yield pos
            if i % side == 0:
                move_to = way2
            else:
                move_to = way1
            distance = ways[move_to]
            move_idx = 0 if move_to in ['l', 'r'] else 1
            other_idx = int(not move_idx)
            pos[move_idx] += distance
            if move_to == way2:
                pos[other_idx] = 0

    @property
    def right(self) -> float:
        return self.interval_x

    @property
    def left(self) -> float:
        return -self.interval_x

    @property
    def top(self) -> float:
        return self.interval_y

    @property
    def bottom(self) -> float:
        return -self.interval_y
