class StringValue:
    def __init__(self, min_length, max_length):
        self.min_length = min_length
        self.max_length = max_length
        self._name = None

    def __set_name__(self, owner, name):
        self._name = f"_{name}"

    def __get__(self, instance, owner):
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        if isinstance(value, str) and self.min_length <= len(value) <= self.max_length:
            setattr(instance, self._name, value)


class PriceValue:
    def __init__(self, max_value):
        self.max_value = max_value
        self._name = None

    def __set_name__(self, owner, name):
        self._name = f"_{name}"

    def __get__(self, instance, owner):
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        if isinstance(value, (int, float)) and 0 <= value <= self.max_value:
            setattr(instance, self._name, value)

class Car:
    name = StringValue(2, 50)
    price = PriceValue(2000000)

    def __init__(self, name, price):
        self.name = name
        self.price = price

class AutoSalon:
    def __init__(self, name: str):
        self.name = name
        self.cars: list[Car] = []

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        if car in self.cars:
            self.cars.remove(car)
        else:
            return self.cars


