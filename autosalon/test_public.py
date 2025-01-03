import unittest
import sys
import subprocess

from autosalon import StringValue, PriceValue, AutoSalon, Car

class TestStringValue(unittest.TestCase):
    def test_valid_string(self):  # 1
        class TestClass:
            name = StringValue(2, 50)
            def __init__(self, name):
                self.name = name

        obj = TestClass("ValidName")
        self.assertEqual(obj.name, "ValidName")

    def test_invalid_string_length(self):
        class TestClass:
            name = StringValue(2, 50)
            def __init__(self, name):
                self.name = name

        obj = TestClass("OK")
        obj.name = "A"  # слишком короткая строка
        self.assertEqual(obj.name, "OK")  # значение не должно измениться

    def test_non_string_value(self):  # 3
        class TestClass:
            name = StringValue(2, 50)
            def __init__(self, name):
                self.name = name

        obj = TestClass("ValidName")
        obj.name = 12345  # не строка
        self.assertEqual(obj.name, "ValidName")  # значение не должно измениться

class TestPriceValue(unittest.TestCase):
    def test_valid_price(self):
        class TestClass:
            price = PriceValue(10000)
            def __init__(self, price):
                self.price = price

        obj = TestClass(9999.99)
        self.assertEqual(obj.price, 9999.99)

    def test_invalid_price_negative(self):  # 5
        class TestClass:
            price = PriceValue(10000)
            def __init__(self, price):
                self.price = price

        obj = TestClass(5000)
        obj.price = -100  # отрицательное значение
        self.assertEqual(obj.price, 5000)  # значение не должно измениться

    def test_invalid_price_over_max(self):
        class TestClass:
            price = PriceValue(10000)
            def __init__(self, price):
                self.price = price

        obj = TestClass(5000)
        obj.price = 15000  # больше максимального значения
        self.assertEqual(obj.price, 5000)  # значение не должно измениться

    def test_non_numeric_price(self):  # 7
        class TestClass:
            price = PriceValue(10000)
            def __init__(self, price):
                self.price = price

        obj = TestClass(5000)
        obj.price = "expensive"  # не числовое значение
        self.assertEqual(obj.price, 5000)  # значение не должно измениться

class TestCar(unittest.TestCase):
    def test_car_creation(self):
        car = Car("Lada", 3000)
        self.assertEqual(car.name, "Lada")
        self.assertEqual(car.price, 3000)

    def test_invalid_car_name(self):  # 9
        car = Car("Lada", 3000)
        car.name = "A"  # слишком короткое имя
        self.assertEqual(car.name, "Lada")  # значение не должно измениться

    def test_invalid_car_price(self):
        car = Car("Lada", 3000)
        car.price = -500  # отрицательная цена
        self.assertEqual(car.price, 3000)  # значение не должно измениться

class TestAutoSalon(unittest.TestCase):  # 11
    def test_autosalon_creation(self):
        salon = AutoSalon("AutoWorld")
        self.assertEqual(salon.name, "AutoWorld")
        self.assertEqual(salon.cars, [])

    def test_add_car(self):
        salon = AutoSalon("AutoWorld")
        car = Car("Nissan", 8000)
        salon.add_car(car)
        self.assertIn(car, salon.cars)

    def test_remove_car(self):  # 13
        salon = AutoSalon("AutoWorld")
        car = Car("Nissan", 8000)
        salon.add_car(car)
        salon.remove_car(car)
        self.assertNotIn(car, salon.cars)

    def test_remove_nonexistent_car(self):
        salon = AutoSalon("AutoWorld")
        car1 = Car("Nissan", 8000)
        car2 = Car("Toyota", 9000)
        salon.add_car(car1)
        salon.remove_car(car2)  # пытаемся удалить машину, которой нет в списке
        self.assertIn(car1, salon.cars)
        self.assertNotIn(car2, salon.cars)

if __name__ == '__main__':
    unittest.main()
