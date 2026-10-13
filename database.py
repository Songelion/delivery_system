import sqlite3
import os
from models import Customer, Order, OrderItem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'delivery.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        CREATE TABLE IF NOT EXISTS customers (\n            id      INTEGER PRIMARY KEY,\n            name    TEXT NOT NULL,\n            phone   TEXT,\n            address TEXT\n        )\n    ')
    cursor.execute("\n        CREATE TABLE IF NOT EXISTS orders (\n            id          INTEGER PRIMARY KEY,\n            customer_id INTEGER REFERENCES customers(id) ON DELETE RESTRICT,\n            order_date  TEXT NOT NULL,\n            status      TEXT NOT NULL CHECK(status IN ('новый', 'в доставке', 'выполнен', 'отменён')),\n            total       REAL NOT NULL\n        )\n    ")
    cursor.execute('\n        CREATE TABLE IF NOT EXISTS order_items (\n            id           INTEGER PRIMARY KEY,\n            order_id     INTEGER REFERENCES orders(id),\n            product_name TEXT,\n            quantity     INTEGER,\n            price        REAL\n        )\n    ')
    conn.commit()
    conn.close()
    print('База данных инициализирована.')

def add_customer(name, phone=None, address=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)', (name, phone, address))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, phone, address FROM customers ORDER BY name')
    rows = cursor.fetchall()
    conn.close()
    return [Customer.from_row(row) for row in rows]

def get_customer_by_id(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, phone, address FROM customers WHERE id = ?', (customer_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return Customer.from_row(row)

def update_customer(customer_id, name=None, phone=None, address=None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    if name is not None:
        fields.append('name = ?')
        values.append(name)
    if phone is not None:
        fields.append('phone = ?')
        values.append(phone)
    if address is not None:
        fields.append('address = ?')
        values.append(address)
    if not fields:
        conn.close()
        return False
    values.append(customer_id)
    cursor.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed

def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM orders WHERE customer_id = ?', (customer_id,))
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        raise ValueError(f'Нельзя удалить клиента id={customer_id}: у него {count} заказ(ов)')
    cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def add_order(customer_id, order_date, status='новый', total=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (customer_id, order_date, status, total) VALUES (?, ?, ?, ?)', (customer_id, order_date, status, total))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, customer_id, order_date, status, total FROM orders ORDER BY order_date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [Order.from_row(row) for row in rows]

def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, customer_id, order_date, status, total FROM orders WHERE id = ?', (order_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return Order.from_row(row)

def get_orders_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, customer_id, order_date, status, total FROM orders WHERE status = ? ORDER BY order_date DESC', (status,))
    rows = cursor.fetchall()
    conn.close()
    return [Order.from_row(row) for row in rows]

def get_orders_by_date(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, customer_id, order_date, status, total FROM orders WHERE order_date >= ? AND order_date <= ? ORDER BY order_date', (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [Order.from_row(row) for row in rows]

def update_order(order_id, customer_id=None, order_date=None, status=None, total=None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    if customer_id is not None:
        fields.append('customer_id = ?')
        values.append(customer_id)
    if order_date is not None:
        fields.append('order_date = ?')
        values.append(order_date)
    if status is not None:
        fields.append('status = ?')
        values.append(status)
    if total is not None:
        fields.append('total = ?')
        values.append(total)
    if not fields:
        conn.close()
        return False
    values.append(order_id)
    cursor.execute(f"UPDATE orders SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed

def delete_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def add_order_item(order_id, product_name, quantity, price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO order_items (order_id, product_name, quantity, price) VALUES (?, ?, ?, ?)', (order_id, product_name, quantity, price))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_items_by_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, order_id, product_name, quantity, price FROM order_items WHERE order_id = ?', (order_id,))
    rows = cursor.fetchall()
    conn.close()
    return [OrderItem.from_row(row) for row in rows]

def delete_order_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM order_items WHERE id = ?', (item_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def report_by_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        SELECT status, COUNT(*) AS count\n        FROM orders\n        GROUP BY status\n        ORDER BY status\n    ')
    rows = cursor.fetchall()
    conn.close()
    return [(row['status'], row['count']) for row in rows]

def report_top_customers(limit=3):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        SELECT \n            customers.name        AS name,\n            SUM(orders.total)     AS total_sum,\n            COUNT(orders.id)      AS orders_count\n        FROM orders\n        JOIN customers ON orders.customer_id = customers.id\n        GROUP BY customers.id\n        ORDER BY total_sum DESC\n        LIMIT ?\n    ', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [(row['name'], row['total_sum'], row['orders_count']) for row in rows]

def report_revenue(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT COALESCE(SUM(total), 0) AS revenue\n        FROM orders\n        WHERE status != 'отменён'\n          AND order_date >= ?\n          AND order_date <= ?\n    ", (start_date, end_date))
    row = cursor.fetchone()
    conn.close()
    return row['revenue']
if __name__ == '__main__':
    init_db()
