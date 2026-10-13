"""
Тесты для модуля data_export.py.
"""

import json
import os
import tempfile

import pytest

from database import (
    add_customer, add_order, add_order_item,
    get_all_orders, get_items_by_order,
)
from data_export import export_to_json, import_from_json


@pytest.fixture
def temp_json_file():
    """Создать временный файл для тестов, удалить после."""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


# ============================================================
# Экспорт
# ============================================================

def test_export_empty(temp_json_file):
    """Экспорт пустой базы — файл создаётся с пустым списком."""
    count = export_to_json(temp_json_file)
    assert count == 0
    
    with open(temp_json_file, encoding='utf-8') as f:
        data = json.load(f)
    assert data == {'orders': []}


def test_export_creates_file(temp_json_file):
    """Экспорт создаёт файл."""
    export_to_json(temp_json_file)
    assert os.path.exists(temp_json_file)


def test_export_with_data(temp_json_file):
    """Экспорт заказов с позициями."""
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 1500.0)
    add_order_item(oid, 'Пицца', 2, 750.0)
    
    count = export_to_json(temp_json_file)
    assert count == 1
    
    with open(temp_json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data['orders']) == 1
    order = data['orders'][0]
    assert order['customer_id'] == c
    assert order['total'] == 1500.0
    assert len(order['items']) == 1
    assert order['items'][0]['product_name'] == 'Пицца'


# ============================================================
# Импорт
# ============================================================

def test_import_nonexistent_file():
    """Импорт несуществующего файла — ошибка."""
    with pytest.raises(FileNotFoundError):
        import_from_json('/tmp/nonexistent_12345.json')


def test_import_invalid_json(temp_json_file):
    """Импорт файла с некорректным JSON."""
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        f.write('не json')
    
    with pytest.raises(json.JSONDecodeError):
        import_from_json(temp_json_file)


def test_import_without_orders_key(temp_json_file):
    """Импорт JSON без ключа 'orders'."""
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        json.dump({'foo': 'bar'}, f)
    
    with pytest.raises(ValueError):
        import_from_json(temp_json_file)


def test_import_orders(temp_json_file):
    """Импорт заказов из JSON."""
    # Сначала создаём клиента (иначе FK не даст создать заказ)
    add_customer('Иван')  # id=1
    
    # Пишем JSON вручную
    data = {
        'orders': [
            {
                'customer_id': 1,
                'order_date': '2025-04-20',
                'status': 'новый',
                'total': 1500.0,
                'items': [
                    {'product_name': 'Пицца', 'quantity': 2, 'price': 750.0}
                ]
            }
        ]
    }
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    count = import_from_json(temp_json_file)
    assert count == 1
    
    # Проверяем, что заказ добавился
    orders = get_all_orders()
    assert len(orders) == 1
    assert orders[0].total == 1500.0


def test_import_skips_invalid_status(temp_json_file):
    """Импорт пропускает заказы с некорректным статусом."""
    add_customer('Иван')
    
    data = {
        'orders': [
            {
                'customer_id': 1,
                'order_date': '2025-04-20',
                'status': 'НЕСУЩЕСТВУЮЩИЙ',
                'total': 1000.0,
                'items': []
            }
        ]
    }
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    count = import_from_json(temp_json_file)
    assert count == 0  # пропущен
    assert len(get_all_orders()) == 0


def test_import_skips_missing_fields(temp_json_file):
    """Импорт пропускает заказы без обязательных полей."""
    add_customer('Иван')
    
    data = {
        'orders': [
            {
                'customer_id': 1,
                # Нет order_date, status, total
            }
        ]
    }
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    count = import_from_json(temp_json_file)
    assert count == 0


# ============================================================
# Экспорт + импорт (round-trip)
# ============================================================

def test_export_import_roundtrip(temp_json_file):
    """Экспорт → импорт сохраняет данные."""
    # Готовим данные
    c = add_customer('Иван')
    oid = add_order(c, '2025-04-20', 'новый', 1500.0)
    add_order_item(oid, 'Пицца', 2, 750.0)
    
    # Экспорт
    export_to_json(temp_json_file)
    
    # Удаляем заказ
    from database import delete_order
    delete_order(oid)
    assert len(get_all_orders()) == 0
    
    # Импорт
    count = import_from_json(temp_json_file)
    assert count == 1
    assert len(get_all_orders()) == 1
