"""Модуль работы с базой данных PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG


# ======================================================================
# Подключение
# ======================================================================
def open_connection():
    """
    Открывает новое подключение к базе данных.

    Возвращает объект соединения psycopg2.
    """
    return psycopg2.connect(**DB_CONFIG)


# ======================================================================
# Чтение данных
# ======================================================================
def select_all(query: str, params: tuple = None) -> list:
    """
    Выполняет SELECT и возвращает все строки.

    Каждая строка представлена словарём (ключ — имя колонки).
    Если записей нет — возвращает пустой список.
    """
    with open_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def select_one(query: str, params: tuple = None):
    """
    Выполняет SELECT и возвращает первую строку.

    Результат представлен словарём или None, если записей нет.
    """
    with open_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()


# ======================================================================
# Изменение данных
# ======================================================================
def run_query(query: str, params: tuple = None) -> int:
    """
    Выполняет INSERT / UPDATE / DELETE.

    Возвращает количество затронутых строк.
    Изменения фиксируются сразу (commit).
    """
    with open_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount


def run_insert_returning(query: str, params: tuple = None):
    """
    Выполняет INSERT с конструкцией RETURNING.

    Возвращает значение из RETURNING (например, id новой записи)
    или None, если строка не была создана.
    """
    with open_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
            row = cursor.fetchone()
            return row[0] if row else None