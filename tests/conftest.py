"""
Настройка pytest: временная база данных для тестов.
Этот файл pytest находит автоматически.
"""

import os
import sys
import pytest


# Добавляем корень проекта в пути поиска модулей
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


# Путь к временной базе
TEST_DB_PATH = os.path.join(BASE_DIR, 'data', 'test_delivery.db')


@pytest.fixture(scope='function', autouse=True)
def clean_db(monkeypatch):
    """
    Перед каждым тестом:
    - подменяем путь к БД на временный,
    - создаём таблицы,
    - после теста удаляем файл.
    
    autouse=True — фикстура применяется ко всем тестам автоматически.
    """
    # Удаляем старую тестовую базу, если осталась
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Подменяем DB_PATH в модуле database
    import database
    monkeypatch.setattr(database, 'DB_PATH', TEST_DB_PATH)
    
    # Создаём таблицы
    database.init_db()
    
    yield  # тут выполняется тест
    
    # После теста удаляем временную базу
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
