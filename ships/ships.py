import random


class Ship:
    def __init__(self, size: int, positions=[]):
        self.size = size
        self.hits = 0
        self.positions = positions

    def place(self, position: list[tuple]):
        self.positions = position

    def is_sunk(self) -> bool:
        return self.hits == self.size

    def hit(self) -> bool:
        self.hits += 1
        return self.is_sunk()


class Battleship(Ship):
    def __init__(self):
        super().__init__(size=4)


class Cruiser(Ship):
    def __init__(self):
        super().__init__(size=3)


class Destroyer(Ship):
    def __init__(self):
        super().__init__(size=2)


class Submarine(Ship):
    def __init__(self):
        super().__init__(size=1)


class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [['#' for _ in range(self.size)] for _ in range(self.size)]
        self.ships = list()

    def is_valid_position(self, positions: list[tuple]) -> bool:
        around = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        for x, y in positions:
            if not (0 <= x < self.size and 0 <= y < self.size):
                return False
            if self.grid[x][y] != '#':
                return False
            for dx, dy in around:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.size and 0 <= new_y < self.size and self.grid[new_x][new_y] == 'S':
                    return False
        return True

    def place_ship(self, ship: Ship, start_row, start_col, horizontal=True):
        if horizontal:
            positions = [(start_row, start_col + i) for i in range(ship.size)]
        else:
            positions = [(start_row + i, start_col) for i in range(ship.size)]

        if not self.is_valid_position(positions):
            return False

        for x, y in positions:
            self.grid[x][y] = 'S'
        ship.place(positions)
        return True

    def receive_shot(self, row, col) -> bool:
        if self.grid[row][col] == 'S':
            self.grid[row][col] = 'X'
            return True
        else:
            self.grid[row][col] = 'O'
        return False

    def display(self) -> None:
        for row in self.grid:
            print(' '.join(row))

    def display_hidden(self):
        for row in self.grid:
            print(' '.join(['#' if cell == 'S' else cell for cell in row]))

    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)


def place_ships_on_board(ships, board):
    for ship in ships:
        board.place_ship(ship, random.randint(0, board.size - 1), random.randint(0, board.size - 1),
                         horizontal=random.choice([True, False]))


