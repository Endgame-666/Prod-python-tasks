import mongomock


class OrderDB:
    def __init__(self, db_name: str = "orders") -> None:
        client = mongomock.MongoClient()
        self.db = client[db_name]
        self.orders = self.db["orders"]

    """
    Описание документа
    
    order_id -- идентификатор заказа
    customer_name -- имя клиента, оформившего заказ
    product -- наименование продукта, который заказан (строка!)
    quantity -- кол-во заказанного товара
    status -- текущий статус заказа
    price -- цена единицы товара
    """

    # !!! для большего погружения, откройте файлик с тестами и посмотрите что должно происходить!!

    def add_order(self, order_id: int, customer_name: str, product: str, quantity: int, status: str,
                  price: float) -> None:
        self.orders.insert_one({
            "order_id": order_id,
            "customer_name": customer_name,
            "product": product,
            "quantity": quantity,
            "status": status,
            "price": price
        })

    def get_order_by_id(self, order_id: int):
        """
        Получить заказ по order_id
        """
        return self.orders.find_one({"order_id": order_id})

    def update_order_status(self, order_id: int, new_status: str) -> None:
        """
        Обновить статус заказа
        """
        self.orders.update_one({"order_id": order_id},
                               {"$set": {"status": new_status}})

    def get_orders_by_customer(self, customer_name: str):
        """
        Получить заказ по заказчику
        """
        return self.orders.find_one({"customer_name": customer_name})

    def delete_order(self, order_id: int) -> None:
        """
        Удалить заказ по ID
        """
        self.orders.delete_one({"order_id": order_id})

    def update_order_quantity(self, order_id: int, new_quantity: int) -> None:
        """
        Обновляем количество товара в заказе.
        """
        self.orders.update_one({"order_id": order_id},
                               {"$set": {"quantity": new_quantity}})

    def get_all_orders(self):
        """
        Возвращаем все заказы в коллекции.
        """
        return list(self.orders.find())

    def get_orders_by_status(self, status: str):
        """
        Возвращаем заказы с указанным статусом.
        """
        return list(self.orders.find({"status": status}))

    def count_orders_by_customer(self, customer_name: str) -> int:
        """
        Возвращаем количество заказов для указанного клиента.
        """
        return len(list(self.orders.find({"customer_name": customer_name})))

    def get_total_quantity_by_customer(self, customer_name: str) -> int:
        """
        Возвращаем общее количество товаров, заказанных клиентом
        """
        customer_orders = list(self.orders.find({"customer_name": customer_name}))
        num = 0
        for order in customer_orders:
            num += order["quantity"]
        return num

    def delete_orders_by_status(self, status: str) -> None:
        """
        Удаляеем все заказы с указанным статусом
        """
        self.orders.delete_many({"status": status})

    def get_total_quantity_per_customer(self):
        """
        Возвращать общее количество товаров, заказанных каждым клиентом
        """
        customer_quantity_list = list()
        customer_names = set()
        for order in self.get_all_orders():
            name_id = order["customer_name"]
            if name_id not in customer_names:
                customer_names.add(name_id)
                customer_quantity_list.append({"_id": name_id,
                                               "total_quantity": order["quantity"],
                                               "total_sales": order["price"] * order["quantity"],
                                               "total_orders": 1})
            else:
                for name in customer_quantity_list:
                    if name["_id"] == name_id:
                        name["total_quantity"] += order["quantity"]
                        name["total_sales"] += order["price"] * order["quantity"]
                        name["total_orders"] += 1
        return customer_quantity_list



    def get_total_sales_by_product(self):
        """
        Возвращать общую сумму продаж для каждого продукта
        """
        product_sales_list = list()
        product_names = set()
        for order in self.get_all_orders():
            name_id = order["product"]
            if name_id not in product_names:
                product_names.add(name_id)
                product_sales_list.append({"_id": name_id,
                                           "total_sales": order["price"] * order["quantity"]}
                                          )
            else:
                for name in product_sales_list:
                    if name["_id"] == name_id:
                        name["total_sales"] += order["price"] * order["quantity"]
        return product_sales_list

    def get_average_order_value_per_customer(self):
        """
        Возвращаем среднюю стоимость заказа для каждого клиента
        """
        order_avg_price_list = list()
        avg_price = self.get_total_quantity_per_customer()
        for name in avg_price:
            order_avg_price_list.append({"_id": name["_id"],
                                         "average_order_value": (name["total_sales"] // name["total_orders"])})
        return order_avg_price_list

    def get_order_count_by_status(self):
        """
        Возвращаем количество заказов в каждом статусе!
        """
        orders_status_list = list()
        product_status = set()
        for order in self.get_all_orders():
            name_id = order["status"]
            if name_id not in product_status:
                product_status.add(name_id)
                orders_status_list.append({"_id": name_id,
                                           "order_count": 1}
                                          )
            else:
                for name in orders_status_list:
                    if name["_id"] == name_id:
                        name["order_count"] += 1
        return orders_status_list

    def get_highest_quantity_order(self):
        """
        Возвращаем заказ с наибольшим количеством товаров
        """
        highest_order = {"order_id": 0, "quantity": 0}
        for order in self.get_all_orders():
            if highest_order["quantity"] < order["quantity"]:
                highest_order["order_id"] = order["order_id"]
                highest_order["quantity"] = order["quantity"]
        return highest_order

