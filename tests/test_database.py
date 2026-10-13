"""
Тесты для модуля database.py.
Используют временную БД (см. conftest.py).
"""

import pytest

from database import (
    add_customer, get_all_customers, get_customer_by_id,
    update_customer, delete_customer,
    add_order, get_all_orders, get_order_by_id,
    get_orders_by_status, get_orders_by_date,
    update_order, delete_order,
    add_order_item, get_items_by_order, delete_order_item,
    report_by_status, report_top_customers, report_revenue,
)


# ============================================================
# Клиенты
# ============================================================

def test_add_customer():
    """Добавление клиента."""
    new_id = add_customer('Иван', '+7-900-111-22-33', 'ул. Ленина, 5')
    assert new_id is not None
    assert new_id > 0


def test_get_all_customers_empty():
    """Пустая база — пустой список."""
    assert get_all_customers() == []


def test_get_all_customers():
    """Все клиенты возвращаются."""
    add_customer('Иван')
    add_customer('Мария')
    customers = get_all_customers()
    assert len(customers) == 2


def test_get_customer_by_id():
    """Получение клиента по id."""
    new_id = add_customer('Иван', '+7-900-111-22-33', 'ул. Ленина, 5')
    c = get_customer_by_id(new_id)
    assert c is not None
    assert c.id == new_id
    assert c.name == 'Иван'


def test_get_customer_by_id_not_found():
    """Несуществующий id — None."""
    assert get_customer_by_id(99999) is None


def test_update_customer():
    """Обновление клиента."""
    new_id = add_customer('Иван')
    result = update_customer(new_id, name='Иван Петров')
    assert result is True
    c = get_customer_by_id(new_id)
    assert c.name == 'Иван Петров'


def test_delete_customer():
    """Удаление клиента без заказов."""
    new_id = add_customer('Иван')
    result = delete_customer(new_id)
    assert result is True
    assert get_customer_by_id(new_id) is None


def test_delete_customer_with_orders():
    """Нельзя удалить клиента с заказами."""
    customer_id = add_customer('Иван')
    add_order(customer_id, '2025-04-20', 'новый', 1000.0)
    
    with pytest.raises(ValueError):
        delete_customer(customer_id)


# ============================================================
# Заказы
# ============================================================

def test_add_order():
    """Добавление заказа."""
    customer_id = add_customer('Иван')
    order_id = add_order(customer_id, '2025-04-20', 'новый', 1500.0)
    assert order_id > 0


def test_get_all_orders():
    """Все заказы возвращаются."""
    c1 = add_customer('Иван')
    c2 = add_customer('Мария')
    add_order(c1, '2025-04-20', 'новый', 1500.0)
    add_order(c2, '2025-04-21', 'выполнен', 2200.0)
    assert len(get_all_orders()) == 2


def test_get_order_by_id():
    """Получение заказа по id."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 1500.0)
    order = get_order_by_id(oid)
    assert order is not None
    assert order.id == oid
    assert order.total == 1500.0


def test_get_orders_by_status():
    """Фильтр по статусу."""
    c = add_customer('Иван')
    add_order(c, '2025-04-20', 'новый', 1500.0)
    add_order(c, '2025-04-21', 'выполнен', 2200.0)
    add_order(c, '2025-04-22', 'новый', 800.0)
    
    new_orders = get_orders_by_status('новый')
    assert len(new_orders) == 2


def test_get_orders_by_date():
    """Фильтр по дате."""
    c = add_customer('Иван')
    add_order(c, '2025-04-15', 'новый', 100.0)
    add_order(c, '2025-04-20', 'новый', 200.0)
    add_order(c, '2025-04-25', 'новый', 300.0)
    
    orders = get_orders_by_date('2025-04-18', '2025-04-22')
    assert len(orders) == 1
    assert orders[0].total == 200.0


def test_update_order():
    """Обновление заказа."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 1500.0)
    
    result = update_order(oid, status='выполнен', total=1600.0)
    assert result is True
    
    order = get_order_by_id(oid)
    assert order.status == 'выполнен'
    assert order.total == 1600.0


def test_delete_order():
    """Удаление заказа."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 1500.0)
    
    result = delete_order(oid)
    assert result is True
    assert get_order_by_id(oid) is None


# ============================================================
# Позиции заказов
# ============================================================

def test_add_order_item():
    """Добавление позиции."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 0.0)
    
    item_id = add_order_item(oid, 'Пицца', 2, 750.0)
    assert item_id > 0


def test_get_items_by_order():
    """Получение позиций заказа."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 0.0)
    add_order_item(oid, 'Пицца', 2, 750.0)
    add_order_item(oid, 'Кола', 1, 200.0)
    
    items = get_items_by_order(oid)
    assert len(items) == 2


def test_delete_order_item():
    """Удаление позиции."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 0.0)
    item_id = add_order_item(oid, 'Пицца', 2, 750.0)
    
    result = delete_order_item(item_id)
    assert result is True
    assert len(get_items_by_order(oid)) == 0


# ============================================================
# Отчёты
# ============================================================

def test_report_by_status():
    """Отчёт по статусам."""
    c = add_customer('Иван')
    add_order(c, '2025-04-20', 'новый', 100.0)
    add_order(c, '2025-04-21', 'новый', 200.0)
    add_order(c, '2025-04-22', 'выполнен', 300.0)
    
    result = dict(report_by_status())
    assert result.get('новый') == 2
    assert result.get('выполнен') == 1


def test_report_top_customers():
    """Топ клиентов по сумме."""
    c1 = add_customer('Иван')
    c2 = add_customer('Мария')
    add_order(c1, '2025-04-20', 'новый', 1000.0)
    add_order(c1, '2025-04-21', 'новый', 500.0)
    add_order(c2, '2025-04-22', 'выполнен', 2000.0)
    
    top = report_top_customers(3)
    assert len(top) == 2
    # Мария (2000) должна быть первой, Иван (1500) — второй
    assert top[0][0] == 'Мария'
    assert top[0][1] == 2000.0


def test_report_revenue():
    """Выручка за период."""
    c = add_customer('Иван')
    add_order(c, '2025-04-20', 'новый', 1500.0)
    add_order(c, '2025-04-21', 'выполнен', 2200.0)
    add_order(c, '2025-04-22', 'отменён', 500.0)  # не должна попасть
    
    revenue = report_revenue('2025-04-01', '2025-04-30')
    assert revenue == 3700.0  # 1500 + 2200 (без отменённого)
