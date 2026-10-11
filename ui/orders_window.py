"""Окно списка заказов (Менеджер / Администратор)"""
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

from config import STYLESHEET, COLOR_BG_SECONDARY, COLOR_ACCENT, COLOR_TEXT
from db import select_all, run_query
from utils.messages import notify_error, notify_success, ask_confirm


class OrdersListDialog(QDialog):
    """
    Список всех заказов.

    Менеджер и администратор могут просматривать, создавать и удалять
    заказы. Редактирование состава доступно только администратору.
    """

    COLUMNS = ('№', 'Дата заказа', 'Клиент', 'Сумма (руб.)')

    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)

        self.current_user = current_user
        self.orders = []

        self.setWindowTitle('Чудо Обувь — Управление заказами')
        self.resize(1000, 650)
        self.setStyleSheet(STYLESHEET)

        self._compose_layout()
        self._reload_orders()

    # ------------------------------------------------------------------
    # Построение интерфейса
    # ------------------------------------------------------------------
    def _compose_layout(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        root.addWidget(self._make_title())
        root.addWidget(self._make_table())
        root.addLayout(self._make_buttons())

    def _make_title(self) -> QLabel:
        title = QLabel('Список заказов')
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
        table.verticalHeader().setDefaultSectionSize(40)
        table.doubleClicked.connect(self._open_selected_order)
        self.orders_table = table
        return table

    def _make_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        row.addWidget(self._button(
            'Открыть заказ', self._open_selected_order
        ))
        row.addWidget(self._button(
            'Создать заказ', self._open_new_order
        ))
        row.addWidget(self._button(
            'Удалить заказ',
            self._delete_selected_order,
            style=self._danger_button_style(),
        ))
        row.addStretch()
        row.addWidget(self._button(
            'Назад',
            self.reject,
            style=self._secondary_button_style(),
        ))

        return row

    def _button(self, text: str, handler, style: str = None) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumHeight(40)
        if style:
            button.setStyleSheet(style)
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

    @staticmethod
    def _danger_button_style() -> str:
        return (
            'QPushButton {'
            '    background-color: #d9534f;'
            '    color: white;'
            '    border: none;'
            '    padding: 10px 22px;'
            '    border-radius: 8px;'
            '    font-weight: bold;'
            '}'
            'QPushButton:hover { background-color: #c9302c; }'
        )

    # ------------------------------------------------------------------
    # Данные
    # ------------------------------------------------------------------
    def _reload_orders(self):
        query = (
            'SELECT o.id, o.order_date, o.client_name, '
            '       COALESCE(SUM(oi.quantity * oi.price_at_moment), 0) AS total '
            'FROM orders o '
            'LEFT JOIN order_items oi ON oi.order_id = o.id '
            'GROUP BY o.id '
            'ORDER BY o.order_date DESC, o.id DESC'
        )
        self.orders = [dict(row) for row in select_all(query)]
        self._render_orders()

    def _render_orders(self):
        self.orders_table.setRowCount(0)
        for row_index, order in enumerate(self.orders):
            self.orders_table.insertRow(row_index)
            self._fill_order_row(row_index, order)

    def _fill_order_row(self, row_index: int, order: dict):
        values = (
            str(order['id']),
            str(order['order_date']),
            order['client_name'],
            '{:,.2f}'.format(float(order['total'])).replace(',', ' '),
        )
        for column_index, text in enumerate(values):
            self.orders_table.setItem(
                row_index, column_index, QTableWidgetItem(text)
            )

    def _selected_order_id(self):
        row_index = self.orders_table.currentRow()
        if row_index < 0:
            return None
        return self.orders[row_index]['id']

    # ------------------------------------------------------------------
    # Действия
    # ------------------------------------------------------------------
    def _open_selected_order(self):
        order_id = self._selected_order_id()
        if order_id is None:
            notify_error(self, 'Выберите заказ')
            return

        from ui.order_view import OrderDetailDialog
        dialog = OrderDetailDialog(
            order_id=order_id,
            current_user=self.current_user,
            parent=self,
        )
        dialog.exec()
        self._reload_orders()

    def _open_new_order(self):
        from ui.new_order_window import NewOrderDialog
        dialog = NewOrderDialog(current_user=self.current_user, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._reload_orders()

    def _delete_selected_order(self):
        order_id = self._selected_order_id()
        if order_id is None:
            notify_error(self, 'Выберите заказ для удаления')
            return

        question = 'Удалить заказ №{}?\nЭто действие необратимо.'.format(order_id)
        if not ask_confirm(self, question):
            return

        try:
            run_query('DELETE FROM orders WHERE id = %s', (order_id,))
            notify_success(self, 'Заказ №{} удалён'.format(order_id))
            self._reload_orders()
        except Exception as error:
            notify_error(self, 'Не удалось удалить заказ:\n{}'.format(error))