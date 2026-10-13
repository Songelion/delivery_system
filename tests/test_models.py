"""
Тесты для модуля models.py.
"""

from models import Customer, Order, OrderItem


# ============================================================
# Customer
# ============================================================

def test_customer_create():
    """Создание клиента."""
    c = Customer(1, 'Иван', '+7-900-111-22-33', 'ул. Ленина, 5')
    assert c.id == 1
    assert c.name == 'Иван'
    assert c.phone == '+7-900-111-22-33'
    assert c.address == 'ул. Ленина, 5'


def test_customer_defaults():
    """Значения по умолчанию."""
    c = Customer()
    assert c.id is None
    assert c.name == ''
    assert c.phone is None
    assert c.address is None


def test_customer_from_row():
    """Создание из строки БД."""
    row = (5, 'Мария', '+7-900-444-55-66', 'пр. Мира, 10')
    c = Customer.from_row(row)
    assert c.id == 5
    assert c.name == 'Мария'


def test_customer_to_dict():
    """Преобразование в словарь."""
    c = Customer(1, 'Иван', '+7-900-111-22-33', 'ул. Ленина, 5')
    d = c.to_dict()
    assert d['id'] == 1
    assert d['name'] == 'Иван'
    assert d['phone'] == '+7-900-111-22-33'
    assert d['address'] == 'ул. Ленина, 5'


def test_customer_str():
    """Строковое представление."""
    c = Customer(1, 'Иван')
    assert 'Customer' in str(c)
    assert 'Иван' in str(c)


# ============================================================
# OrderItem
# ============================================================

def test_order_item_total():
    """Стоимость позиции = quantity * price."""
    item = OrderItem(product_name='Пицца', quantity=2, price=750.0)
    assert item.total == 1500.0


def test_order_item_total_zero():
    """Если quantity=0, то total=0."""
    item = OrderItem(product_name='Пицца', quantity=0, price=750.0)
    assert item.total == 0


def test_order_item_from_row():
    """Создание из строки БД."""
    row = (1, 5, 'Пицца', 2, 750.0)
    item = OrderItem.from_row(row)
    assert item.id == 1
    assert item.order_id == 5
    assert item.product_name == 'Пицца'
    assert item.quantity == 2
    assert item.price == 750.0


def test_order_item_to_dict():
    """Преобразование в словарь."""
    item = OrderItem(1, 5, 'Пицца', 2, 750.0)
    d = item.to_dict()
    assert d['product_name'] == 'Пицца'
    assert d['quantity'] == 2


# ============================================================
# Order
# ============================================================

def test_order_create():
    """Создание заказа."""
    o = Order(1, 1, '2025-04-20', 'новый', 1500.0)
    assert o.id == 1
    assert o.customer_id == 1
    assert o.order_date == '2025-04-20'
    assert o.status == 'новый'
    assert o.total == 1500.0
    assert o.items == []


def test_order_statuses():
    """Допустимые статусы."""
    assert 'новый' in Order.STATUSES
    assert 'в доставке' in Order.STATUSES
    assert 'выполнен' in Order.STATUSES
    assert 'отменён' in Order.STATUSES
    assert len(Order.STATUSES) == 4


def test_order_from_row():
    """Создание из строки БД."""
    row = (3, 2, '2025-04-22', 'выполнен', 2200.0)
    o = Order.from_row(row)
    assert o.id == 3
    assert o.customer_id == 2
    assert o.status == 'выполнен'


def test_order_to_dict_with_items():
    """Словарь заказа с позициями."""
    o = Order(1, 1, '2025-04-20', 'новый', 1500.0)
    o.items.append(OrderItem(1, 1, 'Пицца', 2, 750.0))
    d = o.to_dict()
    assert d['id'] == 1
    assert len(d['items']) == 1
    assert d['items'][0]['product_name'] == 'Пицца'
