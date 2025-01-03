from ships import Ship, Board
import unittest


class TestShip(unittest.TestCase):

    def test_ship_creation(self):  # 1
        ship = Ship(3)
        self.assertEqual(ship.size, 3)
        self.assertEqual(ship.hits, 0)
        self.assertEqual(ship.positions, [])

    def test_ship_place(self):
        ship = Ship(3)
        positions = [(0, 0), (0, 1), (0, 2)]
        ship.place(positions)
        self.assertEqual(ship.positions, positions)

    def test_ship_hit(self):  # 3
        ship = Ship(3)
        ship.hit()
        self.assertEqual(ship.hits, 1)
        self.assertFalse(ship.is_sunk())  # Проверка, что корабль еще не потоплен

        ship.hit()
        ship.hit()
        self.assertTrue(ship.is_sunk())  # После трёх попаданий, корабль должен быть потоплен


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_board_initialization(self):
        self.assertEqual(self.board.size, 10)
        self.assertEqual(len(self.board.grid), 10)
        self.assertEqual(len(self.board.grid[0]), 10)

    def test_place_ship_horizontal(self):  # 5
        ship = Ship(3)
        placed = self.board.place_ship(ship, 0, 0, horizontal=True)
        self.assertTrue(placed)
        self.assertEqual(self.board.grid[0][0], 'S')
        self.assertEqual(self.board.grid[0][1], 'S')
        self.assertEqual(self.board.grid[0][2], 'S')

    def test_place_ship_vertical(self):
        ship = Ship(3)
        placed = self.board.place_ship(ship, 0, 0, horizontal=False)
        self.assertTrue(placed)
        self.assertEqual(self.board.grid[0][0], 'S')
        self.assertEqual(self.board.grid[1][0], 'S')
        self.assertEqual(self.board.grid[2][0], 'S')

    def test_invalid_ship_placement(self):  # 7
        ship = Ship(4)
        placed = self.board.place_ship(ship, 0, 8, horizontal=True)  # Корабль выходит за границу
        self.assertFalse(placed)

    def test_shoot_miss(self):
        missed = self.board.receive_shot(0, 0)
        self.assertFalse(missed)  # Промах
        self.assertEqual(self.board.grid[0][0], 'O')

    def test_shoot_hit(self):  # 9
        ship = Ship(3)
        self.board.place_ship(ship, 0, 0, horizontal=True)
        hit = self.board.receive_shot(0, 0)
        self.assertTrue(hit)  # Попадание
        self.assertEqual(self.board.grid[0][0], 'X')

    def test_all_ships_sunk(self):
        ship1 = Ship(2)
        ship2 = Ship(1)
        self.board.place_ship(ship1, 0, 0, horizontal=True)
        self.board.place_ship(ship2, 2, 2, horizontal=True)

        # Стреляем по всем кораблям
        self.board.receive_shot(0, 0)
        self.board.receive_shot(0, 1)
        self.board.receive_shot(2, 2)

        self.assertTrue(self.board.all_ships_sunk())  # Все корабли должны быть потоплены


if __name__ == '__main__':
    unittest.main()
