import pytest
from deepzon import OrderDB


@pytest.fixture
def order_db():
    db = OrderDB(db_name="orders")
    return db


def test_update_order_quantity(order_db):
    order_db.add_order(1, "Alice", "Laptop", 1, "new", 0.0)
    order_db.update_order_quantity(1, 3)
    result = order_db.get_order_by_id(1)
    assert result["quantity"] == 3


def test_get_all_orders(order_db):
    order_db.add_order(2, "Bob", "Tablet", 1, "new", 0.0)
    order_db.add_order(3, "Alice", "Laptop", 1, "shipped", 0.0)
    orders = order_db.get_all_orders()
    assert len(orders) == 2


def test_get_orders_by_status(order_db):
    order_db.add_order(4, "Alice", "Mouse", 3, "new", 0.0)
    order_db.add_order(5, "Charlie", "Keyboard", 2, "shipped", 0.0)
    new_orders = order_db.get_orders_by_status("new")
    assert len(new_orders) == 1
    assert new_orders[0]["product"] == "Mouse"


def test_count_orders_by_customer(order_db):
    order_db.add_order(6, "Alice", "Monitor", 2, "new", 0.0)
    order_db.add_order(7, "Alice", "Printer", 1, "shipped", 0.0)
    count = order_db.count_orders_by_customer("Alice")
    assert count == 2


def test_get_total_quantity_by_customer(order_db):
    order_db.add_order(8, "Bob", "Tablet", 1, "new", 0.0)
    order_db.add_order(9, "Bob", "Laptop", 2, "shipped", 0.0)
    total_quantity = order_db.get_total_quantity_by_customer("Bob")
    assert total_quantity == 3


def test_delete_orders_by_status(order_db):
    order_db.add_order(10, "Charlie", "Desk", 1, "new", 0.0)
    order_db.add_order(11, "Charlie", "Chair", 1, "new", 0.0)
    order_db.add_order(12, "Charlie", "Lamp", 1, "shipped", 0.0)
    order_db.delete_orders_by_status("new")
    remaining_orders = order_db.get_all_orders()
    assert len(remaining_orders) == 1
    assert remaining_orders[0]["product"] == "Lamp"


def test_get_total_quantity_per_customer(order_db):
    order_db.add_order(1, "Alice", "Laptop", 2, "new", 1000.0)
    order_db.add_order(2, "Alice", "Mouse", 3, "new", 25.0)
    order_db.add_order(3, "Bob", "Tablet", 1, "shipped", 500.0)
    totals = order_db.get_total_quantity_per_customer()
    assert any(total["_id"] == "Alice" and total["total_quantity"] == 5 for total in totals)
    assert any(total["_id"] == "Bob" and total["total_quantity"] == 1 for total in totals)


def test_get_total_sales_by_product(order_db):
    order_db.add_order(1, "Alice", "Laptop", 2, "new", 1000.0)
    order_db.add_order(2, "Bob", "Laptop", 1, "shipped", 1000.0)
    order_db.add_order(3, "Alice", "Mouse", 3, "new", 25.0)
    sales = order_db.get_total_sales_by_product()
    assert any(sale["_id"] == "Laptop" and sale["total_sales"] == 3000.0 for sale in sales)
    assert any(sale["_id"] == "Mouse" and sale["total_sales"] == 75.0 for sale in sales)


def test_get_average_order_value_per_customer(order_db):
    order_db.add_order(1, "Alice", "Laptop", 1, "new", 1000.0)
    order_db.add_order(2, "Alice", "Mouse", 2, "new", 25.0)
    averages = order_db.get_average_order_value_per_customer()
    assert any(avg["_id"] == "Alice" and pytest.approx(avg["average_order_value"], 0.1) == 525.0 for avg in averages)


def test_get_order_count_by_status(order_db):
    order_db.add_order(1, "Alice", "Laptop", 1, "new", 1000.0)
    order_db.add_order(2, "Bob", "Tablet", 2, "shipped", 500.0)
    order_db.add_order(3, "Charlie", "Keyboard", 1, "shipped", 100.0)
    status_counts = order_db.get_order_count_by_status()
    assert any(status["_id"] == "new" and status["order_count"] == 1 for status in status_counts)
    assert any(status["_id"] == "shipped" and status["order_count"] == 2 for status in status_counts)


def test_get_highest_quantity_order(order_db):
    order_db.add_order(1, "Alice", "Laptop", 1, "new", 1000.0)
    order_db.add_order(2, "Bob", "Tablet", 5, "shipped", 500.0)
    highest_quantity_order = order_db.get_highest_quantity_order()
    assert highest_quantity_order["order_id"] == 2
    assert highest_quantity_order["quantity"] == 5
