import json
import os
from database import get_all_orders, get_items_by_order, add_order, add_order_item
from logger_config import setup_logger
log = setup_logger()

def get_orders_with_items():
    orders = get_all_orders()
    result = []
    for order in orders:
        order_dict = order.to_dict()
        items = get_items_by_order(order.id)
        order_dict['items'] = [item.to_dict() for item in items]
        result.append(order_dict)
    return result

def export_to_json(filename):
    data = {'orders': get_orders_with_items()}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    count = len(data['orders'])
    log.info(f'Экспорт {count} заказов в {filename}')
    return count

def import_from_json(filename):
    if not os.path.exists(filename):
        log.error(f'Файл не найден: {filename}')
        raise FileNotFoundError(f'Файл не найден: {filename}')
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'orders' not in data:
        log.error('В файле нет ключа "orders"')
        raise ValueError('Некорректный формат JSON: нет ключа "orders"')
    imported = 0
    skipped = 0
    for order_data in data['orders']:
        try:
            validate_order(order_data)
        except ValueError as e:
            log.warning(f'Пропущен заказ: {e}')
            skipped += 1
            continue
        new_order_id = add_order(customer_id=order_data['customer_id'], order_date=order_data['order_date'], status=order_data['status'], total=order_data['total'])
        for item_data in order_data.get('items', []):
            add_order_item(order_id=new_order_id, product_name=item_data['product_name'], quantity=item_data['quantity'], price=item_data['price'])
        imported += 1
    log.info(f'Импортировано {imported} заказов из {filename} (пропущено: {skipped})')
    return imported

def validate_order(order_data):
    required = ['customer_id', 'order_date', 'status', 'total']
    for field in required:
        if field not in order_data:
            raise ValueError(f'отсутствует поле "{field}"')
    if order_data['status'] not in ('новый', 'в доставке', 'выполнен', 'отменён'):
        raise ValueError(f"некорректный статус: {order_data['status']!r}")
    if not isinstance(order_data['total'], (int, float)):
        raise ValueError(f'total должен быть числом')
    for item in order_data.get('items', []):
        for field in ('product_name', 'quantity', 'price'):
            if field not in item:
                raise ValueError(f'в позиции отсутствует поле "{field}"')
if __name__ == '__main__':
    n = export_to_json('orders_backup.json')
    print(f'Экспортировано: {n} заказов')
    print('Файл orders_backup.json создан в папке проекта.')
