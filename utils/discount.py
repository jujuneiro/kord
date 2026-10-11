"""Расчёт скидки 25% для товаров без заказов за прошлый календарный месяц"""
from datetime import date, timedelta

from db import select_one


# ======================================================================
# Константы
# ======================================================================
NO_ORDERS_DISCOUNT = 25   # скидка для товаров без заказов за прошлый месяц
FULL_PRICE_PERCENT = 100  # база для процентных расчётов


# ======================================================================
# Публичные функции
# ======================================================================
def get_discount_for_product(
    product_id: int,
    reference_date: date = None,
) -> int:
    """
    Возвращает размер скидки в процентах для указанного товара.

    Логика:
        * Если в предыдущем календарном месяце не было ни одного заказа
          на этот товар — применяется скидка 25%.
        * Иначе — скидка 0%.
    """
    anchor_date = reference_date or date.today()

    period_start, period_end = _previous_month_range(anchor_date)
    orders_count = _count_orders_for_product(
        product_id, period_start, period_end
    )

    if orders_count == 0:
        return NO_ORDERS_DISCOUNT
    return 0


def calculate_price_with_discount(price: float, discount: int) -> float:
    """
    Возвращает цену товара с учётом скидки.

    Например, цена 2190 и скидка 25 → 1642.5.
    """
    coefficient = 1 - discount / FULL_PRICE_PERCENT
    return round(price * coefficient, 2)


# ======================================================================
# Внутренние помощники
# ======================================================================
def _previous_month_range(anchor: date) -> tuple:
    """
    Возвращает (первый день, последний день) предыдущего месяца
    относительно указанной даты.
    """
    first_of_current_month = anchor.replace(day=1)
    last_day_of_previous = first_of_current_month - timedelta(days=1)
    first_day_of_previous = last_day_of_previous.replace(day=1)
    return first_day_of_previous, last_day_of_previous


def _count_orders_for_product(
    product_id: int,
    period_start: date,
    period_end: date,
) -> int:
    """Считает количество позиций заказов на товар за указанный период."""
    query = (
        'SELECT COUNT(*) AS cnt '
        'FROM order_items oi '
        'JOIN orders o ON o.id = oi.order_id '
        'WHERE oi.product_id = %s '
        '  AND o.order_date BETWEEN %s AND %s'
    )
    row = select_one(query, (product_id, period_start, period_end))
    return row['cnt']