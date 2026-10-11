"""Диалоговое окно корзины с оформлением заказа"""
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt

from config import STYLESHEET, COLOR_ACCENT
from db import run_query, run_insert_returning
from utils.messages import (
    notify_error,
    notify_warning,
    notify_success,
    ask_confirm,
)


class CartDialog(QDialog):
    """Диалог корзины: показывает позиции и оформляет заказ."""

    COLUMNS = (
        'ID',
        'Наименование',
        'Производитель',
        'Размер',
        'Кол-во',
        'Сумма (руб.)',
    )

    def __init__(self, current_user: dict, basket: list, parent=None):
        super().__init__(parent)

        self.current_user = current_user
        self.basket = basket

        self.setWindowTitle('Чудо Обувь — Корзина')
        self.resize(1000, 650)
        self.setStyleSheet(STYLESHEET)

        self._compose_layout()
        self._render_basket()

    # ------------------------------------------------------------------
    # Построение интерфейса
    # ------------------------------------------------------------------
    def _compose_layout(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        root.addWidget(self._make_title())
        root.addWidget(self._make_table())
        root.addWidget(self._make_total_label())
        root.addLayout(self._make_buttons())

    def _make_title(self) -> QLabel:
        title = QLabel('Корзина и оформление заказа')
        title.setStyleSheet(
            'font-size: 20px; font-weight: bold; color: {};'.format(COLOR_ACCENT)
        )
        return title

    def _make_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(self.COLUMNS))
        table.setHorizontalHeaderLabels(list(self.COLUMNS))
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setDefaultSectionSize(38)
        self.basket_table = table
        return table

    def _make_total_label(self) -> QLabel:
        label = QLabel('Итого к оплате: 0.00 руб.')
        label.setStyleSheet('font-size: 16px; font-weight: bold;')
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.grand_total_label = label
        return label

    def _make_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        row.addWidget(self._button(
            'Удалить позицию', self._drop_selected_item
        ))
        row.addWidget(self._button(
            'Очистить', self._empty_basket, secondary=True
        ))
        row.addWidget(self._button(
            'Оформить заказ', self._place_order
        ))
        row.addStretch()
        row.addWidget(self._button(
            'Назад', self.reject, secondary=True
        ))

        return row

    def _button(self, text: str, handler, secondary: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumHeight(40)
        if secondary:
            button.setStyleSheet(self._secondary_button_style())
        button.clicked.connect(handler)
        return button

    @staticmethod
    def _secondary_button_style() -> str:
        return (
            'QPushButton {'
            '    background-color: #D2F6E7;'
            '    color: #2c3e50;'
            '    border: 2px solid #70B2AF;'
            '    padding: 10px 22px;'
            '    border-radius: 8px;'
            '    font-weight: bold;'
            '}'
            'QPushButton:hover { background-color: #BBEBD7; }'
        )

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------
    def _render_basket(self):
        self.basket_table.setRowCount(0)
        running_total = 0.0

        for row_index, position in enumerate(self.basket):
            line_sum = position['price'] * position['quantity']
            running_total += line_sum

            self.basket_table.insertRow(row_index)
            self._fill_row(row_index, position, line_sum)

        self.grand_total_label.setText(
            'Итого к оплате: {:.2f} руб.'.format(running_total).replace(',', ' ')
        )

    def _fill_row(self, row_index: int, position: dict, line_sum: float):
        values = (
            str(position['product_id']),
            position['name'],
            position.get('manufacturer', ''),
            str(position['size_value']),
            str(position['quantity']),
            '{:.2f}'.format(line_sum),
        )
        for column_index, text in enumerate(values):
            self.basket_table.setItem(
                row_index, column_index, QTableWidgetItem(text)
            )

    # ------------------------------------------------------------------
    # Операции над корзиной
    # ------------------------------------------------------------------
    def _drop_selected_item(self):
        row_index = self.basket_table.currentRow()
        if row_index < 0:
            notify_warning(self, 'Выберите строку для удаления')
            return

        self.basket.pop(row_index)
        self._render_basket()

    def _empty_basket(self):
        if not self.basket:
            return
        if ask_confirm(self, 'Очистить всю корзину?'):
            self.basket.clear()
            self._render_basket()

    # ------------------------------------------------------------------
    # Оформление заказа
    # ------------------------------------------------------------------
    def _place_order(self):
        if not self._validate_before_order():
            return

        if not ask_confirm(self, 'Оформить заказ?'):
            return

        try:
            self._save_order_to_database()
        except Exception as err:
            notify_error(self, 'Не удалось оформить заказ:\n{}'.format(err))

    def _validate_before_order(self) -> bool:
        if not self.basket:
            notify_error(self, 'Корзина пуста')
            return False

        if not self.current_user or not self.current_user.get('id'):
            notify_error(self, 'Для оформления заказа нужна авторизация')
            return False

        return True

    def _save_order_to_database(self):
        order_id = self._create_order_header()

        for position in self.basket:
            self._reserve_stock(position)
            self._attach_order_item(order_id, position)

        notify_success(self, 'Заказ №{} успешно оформлен!'.format(order_id))
        self.basket.clear()
        self.accept()

    def _create_order_header(self) -> int:
        return run_insert_returning(
            'INSERT INTO orders (order_date, user_id, client_name) '
            'VALUES (CURRENT_DATE, %s, %s) RETURNING id',
            (self.current_user['id'], self.current_user['full_name']),
        )

    def _reserve_stock(self, position: dict):
        affected = run_query(
            'UPDATE stock_items '
            'SET quantity_available = quantity_available - %s '
            'WHERE product_id = %s AND size_id = %s '
            '  AND quantity_available >= %s',
            (
                position['quantity'],
                position['product_id'],
                position['size_id'],
                position['quantity'],
            ),
        )
        if affected == 0:
            raise Exception(
                'Недостаточно товара: {} (размер {})'.format(
                    position['name'], position['size_value']
                )
            )

    def _attach_order_item(self, order_id: int, position: dict):
        run_query(
            'INSERT INTO order_items '
            '(order_id, product_id, size_id, quantity, price_at_moment) '
            'VALUES (%s, %s, %s, %s, %s)',
            (
                order_id,
                position['product_id'],
                position['size_id'],
                position['quantity'],
                position['price'],
            ),
        )