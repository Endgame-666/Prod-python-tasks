from enum import Enum


class TurnDirection(Enum):
    RIGHT = 1
    LEFT = -1


class Direction(Enum):
    NORTH = 'N'
    SOUTH = 'S'
    EAST = 'E'
    WEST = 'W'


class SensorDirection(Enum):
    FRONT = "front"
    LEFT = 'left'
    RIGHT = 'right'


class Movement(Enum):
    FORWARD = 1
    BACKWARD = -1


class VacuumCleaner:
    def __init__(self) -> None:
         self.dust_collected = 0  # Собранная пыль

    def vacuum(self):
         """Метод для всасывания пыли"""
         self.dust_collected += 1
         print(f"Впитывание пыли... Собрано {self.dust_collected} единиц пыли.")

# Базовый класс для машины на радиоуправлении
class RemoteControlCar:
    def __init__(self) -> None:
         self.position = [0, 0]  # Начальная позиция
         self.direction = Direction.NORTH  # Направление: N, E, S, W

    def turn(self, turn_to: TurnDirection) -> None:
        if not isinstance(turn_to, TurnDirection):
            raise AttributeError("Некорректное движение")
        directions = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]
        if turn_to == TurnDirection.RIGHT:
            self.direction = directions[(directions.index(self.direction) - 1) % 4]
            print(f"Поворот направо. Теперь направление: {self.direction}")
        elif turn_to == TurnDirection.LEFT:
            self.direction = directions[(directions.index(self.direction) + 1) % 4]
            print(f"Поворот налево. Теперь направление: {self.direction}")

    def move(self, distance: int, move_to: Movement) -> None:
        if not isinstance(move_to, Movement):
            raise AttributeError("Некорректное движение")
        if move_to == Movement.BACKWARD:
            if self.direction == Direction.NORTH:
                self.position[1] -= distance
            elif self.direction == Direction.EAST:
                self.position[0] -= distance
            elif self.direction == Direction.SOUTH:
                self.position[1] += distance
            elif self.direction == Direction.WEST:
                self.position[0] += distance
            print(f"Двигаемся назад на {distance} единиц. Позиция: {self.position}")
        elif move_to == Movement.FORWARD:
            if self.direction == Direction.NORTH:
                self.position[1] += distance
            elif self.direction == Direction.WEST:
                self.position[0] -= distance
            elif self.direction == Direction.SOUTH:
                self.position[1] -= distance
            elif self.direction == Direction.EAST:
                self.position[0] += distance
            print(f"Двигаемся вперед на {distance} единиц. Позиция: {self.position}")


# Класс для автономного движения
class AutonomousMovement(RemoteControlCar):
    def __init__(self) -> None:
        RemoteControlCar.__init__(self)
        self.sensors = {SensorDirection.FRONT: False, SensorDirection.LEFT: False, SensorDirection.RIGHT: False}  # Ложь означает, что препятствий нет

    def detect_obstacle(self, direction: SensorDirection) -> bool:
        """Метод для распознавания препятствия"""
        return self.sensors[direction]

    def auto_move(self) -> None:
        """Метод для автономного движения"""
        if not self.detect_obstacle(SensorDirection.FRONT):
            print("Препятствий впереди нет, едем вперед.")
            self.move(1, Movement.FORWARD)
        else:
            print("Обнаружено препятствие! Пытаемся объехать...")
            if not self.detect_obstacle(SensorDirection.LEFT):
                self.turn(TurnDirection.LEFT)
                self.move(1, Movement.FORWARD)
            elif not self.detect_obstacle(SensorDirection.RIGHT):
                self.turn(TurnDirection.RIGHT)
                self.move(1, Movement.FORWARD)
            else:
                print("Заблокирован со всех сторон. Остановка.")

 # Итоговый класс автономного робота для уборки
class AutonomousCleaningRobot(VacuumCleaner , AutonomousMovement):
    def __init__(self) -> None:
        VacuumCleaner.__init__(self)
      #  RemoteControlCar.__init__(self)
        AutonomousMovement.__init__(self)

    def clean_and_move(self) -> None:
        """Метод для автономной уборки и движения"""
        print("Начинаем уборку...")
        self.vacuum()  # Включаем всасывание
        self.auto_move()  # Автономное движение