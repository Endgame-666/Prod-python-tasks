import unittest

from robot_vacuum_cleaner import (
    AutonomousCleaningRobot,
    Direction,
    Movement,
    TurnDirection,
    SensorDirection,
)

class TestAutonomousCleaningRobotMovement(unittest.TestCase):

    def setUp(self):
        # Инициализируем робота перед каждым тестом
        self.robot = AutonomousCleaningRobot()

    def test_initial_position(self):  # 1
        # Проверяем начальную позицию и направление
        self.assertEqual(self.robot.position, [0, 0])
        self.assertEqual(self.robot.direction, Direction.NORTH)

    def test_move_forward(self):
        # Робот движется вперед на 3 единицы
        self.robot.move(3, Movement.FORWARD)
        self.assertEqual(self.robot.position, [0, 3])

    def test_move_backward(self):  # 3
        # Робот движется назад на 2 единицы
        self.robot.move(2, Movement.BACKWARD)
        self.assertEqual(self.robot.position, [0, -2])

    def test_turn_left_and_move_forward(self):
        # Поворот налево и движение вперед
        self.robot.turn(TurnDirection.LEFT)
        self.robot.move(4, Movement.FORWARD)
        self.assertEqual(self.robot.direction, Direction.WEST)
        self.assertEqual(self.robot.position, [-4, 0])

    def test_turn_right_and_move_forward(self):  # 5
        # Поворот направо и движение вперед
        self.robot.turn(TurnDirection.RIGHT)
        self.robot.move(5, Movement.FORWARD)
        self.assertEqual(self.robot.direction, Direction.EAST)
        self.assertEqual(self.robot.position, [5, 0])

    def test_move_in_square(self):
        # Робот движется по квадрату и возвращается в исходную точку
        for _ in range(4):
            self.robot.move(2, Movement.FORWARD)
            self.robot.turn(TurnDirection.RIGHT)
        self.assertEqual(self.robot.position, [0, 0])
        self.assertEqual(self.robot.direction, Direction.NORTH)

    def test_multiple_turns(self):  # 7
        # Проверяем, что после 4 поворотов направо робот смотрит на север
        for _ in range(4):
            self.robot.turn(TurnDirection.RIGHT)
        self.assertEqual(self.robot.direction, Direction.NORTH)

    def test_autonomous_movement_with_obstacle(self):
        # Устанавливаем препятствие спереди и проверяем автономное движение
        self.robot.sensors[SensorDirection.FRONT] = True
        self.robot.auto_move()
        # Ожидаем, что робот повернет и переместится
        self.assertNotEqual(self.robot.direction, Direction.NORTH)
        self.assertNotEqual(self.robot.position, [0, 0])

class TestAutonomousCleaningRobotMethods(unittest.TestCase):

    def setUp(self):
        self.robot = AutonomousCleaningRobot()

    def test_vacuum_once(self):  # 9
        # Проверяем работу метода vacuum
        self.robot.vacuum()
        self.assertEqual(self.robot.dust_collected, 1)

    def test_vacuum_multiple_times(self):
        # Проверяем накопление пыли
        for _ in range(5):
            self.robot.vacuum()
        self.assertEqual(self.robot.dust_collected, 5)

    def test_detect_obstacle_front(self):  # 11
        # Проверяем обнаружение препятствия спереди
        self.robot.sensors[SensorDirection.FRONT] = True
        self.assertTrue(self.robot.detect_obstacle(SensorDirection.FRONT))

    def test_detect_no_obstacle(self):
        # Проверяем отсутствие препятствий
        self.assertFalse(self.robot.detect_obstacle(SensorDirection.LEFT))
        self.assertFalse(self.robot.detect_obstacle(SensorDirection.RIGHT))

    def test_clean_and_move_no_obstacles(self):  # 13
        # Проверяем работу clean_and_move без препятствий
        self.robot.clean_and_move()
        self.assertEqual(self.robot.dust_collected, 1)
        self.assertEqual(self.robot.position, [0, 1])

    def test_clean_and_move_with_obstacle(self):
        # Проверяем работу clean_and_move с препятствием спереди
        self.robot.sensors[SensorDirection.FRONT] = True
        self.robot.clean_and_move()
        self.assertEqual(self.robot.dust_collected, 1)
        self.assertNotEqual(self.robot.direction, Direction.NORTH)
        self.assertNotEqual(self.robot.position, [0, 1])

    def test_move_invalid_movement(self):  # 15
        # Проверяем реакцию на некорректное движение
        with self.assertRaises(AttributeError):
            self.robot.move(3, "FORWARD")  # Некорректный тип движения

    def test_turn_invalid_direction(self):
        # Проверяем реакцию на некорректный поворот
        with self.assertRaises(AttributeError):
            self.robot.turn("LEFT")  # Некорректный тип поворота

class TestEnums(unittest.TestCase):

    def test_direction_values(self):  # 17
        # Проверяем значения Direction
        self.assertEqual(Direction.NORTH.value, "N")
        self.assertEqual(Direction.EAST.value, "E")
        self.assertEqual(Direction.SOUTH.value, "S")
        self.assertEqual(Direction.WEST.value, "W")

    def test_sensor_direction_values(self):
        # Проверяем значения SensorDirection
        self.assertEqual(SensorDirection.FRONT.value, "front")
        self.assertEqual(SensorDirection.LEFT.value, "left")
        self.assertEqual(SensorDirection.RIGHT.value, "right")

    def test_movement_values(self):  # 19
        # Проверяем значения Movement
        self.assertEqual(Movement.FORWARD.value, 1)
        self.assertEqual(Movement.BACKWARD.value, -1)

    def test_turn_direction_values(self):
        # Проверяем значения TurnDirection
        self.assertEqual(TurnDirection.LEFT.value, -1)
        self.assertEqual(TurnDirection.RIGHT.value, 1)

    def test_direction_enum_membership(self):  # 21
        # Проверяем наличие членов в Direction
        self.assertIn(Direction.NORTH, Direction)
        self.assertIn(Direction.EAST, Direction)

    def test_sensor_direction_enum_membership(self):
        # Проверяем наличие членов в SensorDirection
        self.assertIn(SensorDirection.FRONT, SensorDirection)
        self.assertIn(SensorDirection.LEFT, SensorDirection)

    def test_invalid_enum_access(self):  #23
        # Проверяем реакцию на неверный доступ к Enum
        with self.assertRaises(AttributeError):
            _ = Direction.UP

    def test_enum_type(self):
        # Проверяем, что перечисления являются Enum
        self.assertIsInstance(Direction.NORTH, Direction)
        self.assertIsInstance(Movement.FORWARD, Movement)

if __name__ == '__main__':
    unittest.main()