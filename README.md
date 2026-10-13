# Система учёта заказов «Быстрая доставка»

Внутреннее приложение для учёта заказов компании «Быстрая доставка».

## Возможности

- Управление клиентами (CRUD, защита от удаления клиента с заказами)
- Управление заказами (CRUD, фильтрация по статусу и дате)
- Список товаров в заказе
- Отчёты: заказы по статусам, топ-3 клиента, выручка за период
- Экспорт/импорт заказов в JSON
- CLI-режим (argparse)
- GUI-режим (Tkinter)

## Технологии

- Python 3.8+
- SQLite
- Tkinter
- argparse
- pytest
- logging

## Структура проекта

- main_cli.py — CLI-точка входа
- main_gui.py — GUI-точка входа
- database.py — работа с БД
- models.py — классы Customer, Order, OrderItem
- data_export.py — экспорт/импорт JSON
- logger_config.py — логирование
- tests/ — тесты pytest
- logs/ — логи
- data/ — база данных
- requirements.txt — зависимости

## Установка

    pip3 install -r requirements.txt

## Использование

### CLI

    python3 main_cli.py report --period month
    python3 main_cli.py export --file orders.json
    python3 main_cli.py import --file orders.json

### GUI

    python3 main_gui.py

### Тесты

    python3 -m pytest tests/ -v

## База данных

- customers — клиенты (id, name, phone, address)
- orders — заказы (id, customer_id, order_date, status, total)
- order_items — позиции (id, order_id, product_name, quantity, price)

## Тесты

44 теста: test_models.py, test_database.py, test_export.py.
Покрытие: > 60%.