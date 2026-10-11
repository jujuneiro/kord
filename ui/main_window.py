"""Главное окно приложения — каталог обуви"""
import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QLineEdit,
    QComboBox,
    QPushButton,
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from config import (
    RESOURCES_DIR,
    STYLESHEET,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT,
    COLOR_TEXT,
    LOGO_HEIGHT_HEADER,
    CARDS_SPACING,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from db import select_all
from ui.product_card import ProductCard
from utils.discount import get_discount_for_product


class CatalogWindow(QMainWindow):
    """Главное окно с каталогом товаров."""

    SORT_VARIANTS = ('Без сортировки', 'Цена ↑', 'Цена ↓')
    MANAGER_ROLES = ('Администратор', 'Менеджер')

    def __init__(self, current_user: dict = None):
        super().__init__()

        self.current_user = current_user
        self.basket = []
        self.catalog_items = []

        self.setWindowTitle('Чудо Обувь — Каталог')
        self.resize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(STYLESHEET)
        self._apply_window_icon()

        self._compose_layout()
        self._load_catalog()

    # ------------------------------------------------------------------
    # Внешний вид
    # ------------------------------------------------------------------
    def _apply_window_icon(self):
        icon_path = os.path.join(RESOURCES_DIR, 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _compose_layout(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        root.addLayout(self._build_header())
        root.addWidget(self._build_filter_panel())
        root.addWidget(self._build_catalog_scroll(), 1)

    def _build_header(self) -> QHBoxLayout:
        """Шапка: логотип, ФИО, кнопки."""
        row = QHBoxLayout()
        row.setSpacing(12)

        self._add_logo(row)
        row.addStretch()
        self._add_user_label(row)
        self._add_action_buttons(row)

        return row

    def _add_logo(self, row: QHBoxLayout):
        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if not os.path.exists(logo_path):
            return

        logo = QLabel()
        logo.setPixmap(
            QPixmap(logo_path).scaledToHeight(
                LOGO_HEIGHT_HEADER,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        row.addWidget(logo)

    def _add_user_label(self, row: QHBoxLayout):
        if not self.current_user:
            return

        label = QLabel(self.current_user.get('full_name', ''))
        label.setStyleSheet(
            'font-size: 15px; font-weight: bold; color: {};'.format(COLOR_TEXT)
        )
        row.addWidget(label)

    def _add_action_buttons(self, row: QHBoxLayout):
        if not self.current_user:
            return

        if self.current_user.get('id'):
            self.basket_button = QPushButton('Корзина')
            self.basket_button.clicked.connect(self._open_basket)
            row.addWidget(self.basket_button)

        if self.current_user.get('role_name') in self.MANAGER_ROLES:
            orders_btn = QPushButton('Управление заказами')
            orders_btn.clicked.connect(self._open_orders_window)
            row.addWidget(orders_btn)

        logout_btn = QPushButton('Выйти')
        logout_btn.setStyleSheet(self._secondary_button_style())
        logout_btn.clicked.connect(self._sign_out)
        row.addWidget(logout_btn)

    def _build_filter_panel(self) -> QWidget:
        """Панель фильтров в дополнительном фоне."""
        panel = QWidget()
        panel.setStyleSheet(
            'background-color: {};'
            'border-radius: 12px;'
            'padding: 4px;'.format(COLOR_BG_SECONDARY)
        )

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        self.search_field = self._make_search_field(layout)
        self.category_filter = self._make_category_filter(layout)
        self.sort_filter = self._make_sort_filter(layout)

        panel.setVisible(self.current_user is not None)
        return panel

    def _make_search_field(self, layout: QHBoxLayout) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText('Поиск по наименованию или описанию...')
        field.textChanged.connect(self._refresh_visible_items)

        layout.addWidget(QLabel('Поиск:'))
        layout.addWidget(field, 2)
        return field

    def _make_category_filter(self, layout: QHBoxLayout) -> QComboBox:
        combo = QComboBox()
        combo.addItem('Все категории', None)
        combo.currentIndexChanged.connect(self._refresh_visible_items)

        layout.addWidget(QLabel('Категория:'))
        layout.addWidget(combo, 1)
        return combo

    def _make_sort_filter(self, layout: QHBoxLayout) -> QComboBox:
        combo = QComboBox()
        combo.addItems(list(self.SORT_VARIANTS))
        combo.currentIndexChanged.connect(self._refresh_visible_items)

        layout.addWidget(QLabel('Сортировка:'))
        layout.addWidget(combo, 1)
        return combo

    def _build_catalog_scroll(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_layout.setSpacing(CARDS_SPACING)

        scroll.setWidget(self.cards_container)
        return scroll

    # ------------------------------------------------------------------
    # Данные
    # ------------------------------------------------------------------
    def _load_catalog(self):
        query = (
            'SELECT p.*, COALESCE(SUM(si.quantity_available), 0) '
            '       AS total_quantity '
            'FROM products p '
            'LEFT JOIN stock_items si ON si.product_id = p.id '
            'GROUP BY p.id '
            'ORDER BY p.name'
        )
        self.catalog_items = [dict(row) for row in select_all(query)]
        self._populate_categories()
        self._refresh_visible_items()

    def _populate_categories(self):
        categories = sorted({item['category'] for item in self.catalog_items})
        for category in categories:
            self.category_filter.addItem(category, category)

    def _refresh_visible_items(self):
        visible = list(self.catalog_items)
        visible = self._filter_by_category(visible)
        visible = self._filter_by_text(visible)
        visible = self._sort_items(visible)
        self._render_cards(visible)

    def _filter_by_category(self, items: list) -> list:
        selected = self.category_filter.currentData()
        if not selected:
            return items
        return [i for i in items if i['category'] == selected]

    def _filter_by_text(self, items: list) -> list:
        query = self.search_field.text().strip().lower()
        if not query:
            return items

        result = []
        for item in items:
            name_match = query in item['name'].lower()
            desc_match = query in (item.get('description') or '').lower()
            if name_match or desc_match:
                result.append(item)
        return result

    def _sort_items(self, items: list) -> list:
        mode = self.sort_filter.currentText()
        if mode == 'Цена ↑':
            return sorted(items, key=lambda i: float(i['price']))
        if mode == 'Цена ↓':
            return sorted(items, key=lambda i: float(i['price']), reverse=True)
        return items

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------
    def _render_cards(self, items: list):
        self._clear_cards_container()
        if not items:
            self.cards_layout.addWidget(QLabel('Товары не найдены'))
            return
        for item in items:
            self._append_card(item)

    def _clear_cards_container(self):
        while self.cards_layout.count():
            layout_item = self.cards_layout.takeAt(0)
            widget = layout_item.widget()
            if widget:
                widget.deleteLater()

    def _append_card(self, item: dict):
        discount = get_discount_for_product(item['id'])
        card = ProductCard(item, discount)
        card.clicked.connect(self._open_product_card)
        self.cards_layout.addWidget(card)

    # ------------------------------------------------------------------
    # Действия
    # ------------------------------------------------------------------
    def _open_product_card(self, product_id: int):
        if not self.current_user or not self.current_user.get('id'):
            from utils.messages import notify_success
            notify_success(self, 'Для оформления заказа войдите в систему')
            return

        from ui.product_view import ProductViewDialog
        dialog = ProductViewDialog(product_id, self.basket, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._update_basket_button()

    def _open_basket(self):
        from ui.cart_widget import CartDialog
        dialog = CartDialog(self.current_user, self.basket, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._load_catalog()
            self._update_basket_button()

    def _open_orders_window(self):
        from ui.orders_window import OrdersListDialog
        dialog = OrdersListDialog(current_user=self.current_user, parent=self)
        dialog.exec()
        self._load_catalog()

    def _sign_out(self):
        from ui.login_window import AuthDialog

        self.close()
        login = AuthDialog()

        if login.exec() == login.DialogCode.Accepted:
            reopened = CatalogWindow(current_user=login.get_profile())
            reopened.show()
            self._reopened_window = reopened

    # ------------------------------------------------------------------
    # Обновление интерфейса
    # ------------------------------------------------------------------
    def _update_basket_button(self):
        if not hasattr(self, 'basket_button'):
            return

        if not self.basket:
            self.basket_button.setText('Корзина')
            return

        total_quantity = sum(item['quantity'] for item in self.basket)
        self.basket_button.setText('Корзина ({})'.format(total_quantity))

    @staticmethod
    def _secondary_button_style() -> str:
        """Стиль светлой (вторичной) кнопки."""
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