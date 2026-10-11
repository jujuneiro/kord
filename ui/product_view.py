"""Диалог просмотра товара и добавления его в корзину"""
import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
    QTextEdit,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from config import (
    PRODUCTS_IMG_DIR,
    RESOURCES_DIR,
    STYLESHEET,
    COLOR_ACCENT,
    COLOR_TEXT_MUTED,
    CARD_IMAGE_SIZE,
    CARD_BORDER_RADIUS,
)
from db import select_one, select_all
from utils.discount import (
    get_discount_for_product,
    calculate_price_with_discount,
)
from utils.messages import notify_error, notify_success


class ProductViewDialog(QDialog):
    """Диалог подробного просмотра товара."""

    DESCRIPTION_MAX_HEIGHT = 100

    def __init__(self, product_id: int, basket: list, parent=None):
        super().__init__(parent)

        self.product_id = product_id
        self.basket = basket
        self.product = {}
        self.sizes = []
        self.discount = 0

        self.setWindowTitle('Чудо Обувь — Просмотр товара')
        self.resize(760, 760)
        self.setStyleSheet(STYLESHEET)

        self._load_data()
        self._compose_layout()

    # ------------------------------------------------------------------
    # Данные
    # ------------------------------------------------------------------
    def _load_data(self):
        product_row = select_one(
            'SELECT * FROM products WHERE id = %s',
            (self.product_id,),
        )
        self.product = dict(product_row)

        query_sizes = (
            'SELECT s.id AS size_id, s.value, si.quantity_available '
            'FROM stock_items si '
            'JOIN sizes s ON s.id = si.size_id '
            'WHERE si.product_id = %s AND si.quantity_available > 0 '
            'ORDER BY s.value'
        )
        self.sizes = [
            dict(row) for row in select_all(query_sizes, (self.product_id,))
        ]

        self.discount = get_discount_for_product(self.product_id)

    # ------------------------------------------------------------------
    # Интерфейс
    # ------------------------------------------------------------------
    def _compose_layout(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        root.addWidget(self._make_image())
        root.addWidget(self._make_manufacturer_title())
        root.addWidget(self._make_category_label())
        root.addWidget(self._make_composition_label())
        root.addWidget(self._make_description_view())
        root.addWidget(self._make_price_label())
        root.addLayout(self._make_size_and_quantity_row())
        root.addStretch()
        root.addLayout(self._make_footer_buttons())

    def _make_image(self) -> QLabel:
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = self._load_product_pixmap()
        image_label.setPixmap(
            pixmap.scaled(
                CARD_IMAGE_SIZE * 2,
                CARD_IMAGE_SIZE * 2,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        return image_label

    def _make_manufacturer_title(self) -> QLabel:
        label = QLabel(
            '<b>{} | {}</b>'.format(
                self.product.get('manufacturer', ''),
                self.product.get('name', ''),
            )
        )
        label.setStyleSheet('font-size: 18px;')
        return label

    def _make_category_label(self) -> QLabel:
        return QLabel('Категория: {}'.format(self.product.get('category', '')))

    def _make_composition_label(self) -> QLabel:
        label = QLabel('Состав: {}'.format(self.product.get('composition', '')))
        label.setWordWrap(True)
        return label

    def _make_description_view(self) -> QTextEdit:
        description = QTextEdit(self.product.get('description') or '')
        description.setReadOnly(True)
        description.setMaximumHeight(self.DESCRIPTION_MAX_HEIGHT)
        return description

    def _make_price_label(self) -> QLabel:
        final_price = calculate_price_with_discount(
            float(self.product['price']), self.discount
        )
        html = '<b style="color: {}; font-size: 18px;">Цена со скидкой: {:.2f} ₽</b>'.format(
            COLOR_ACCENT, final_price
        )
        if self.discount > 0:
            html += (
                ' <span style="color:{};text-decoration:line-through;">'
                '{:.2f} ₽'
                '</span>'
            ).format(COLOR_TEXT_MUTED, float(self.product['price']))
        label = QLabel(html)
        label.setTextFormat(Qt.TextFormat.RichText)
        return label

    def _make_size_and_quantity_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        row.addWidget(QLabel('Размер:'))
        self.size_combo = self._make_size_combo()
        row.addWidget(self.size_combo, 2)

        row.addWidget(QLabel('Кол-во:'))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(1)
        self.quantity_spin.setMinimumHeight(38)
        row.addWidget(self.quantity_spin, 1)

        self.size_combo.currentIndexChanged.connect(self._sync_max_quantity)
        self._sync_max_quantity()

        return row

    def _make_size_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.setMinimumHeight(38)

        if not self.sizes:
            combo.addItem('Нет в наличии', None)
            combo.setEnabled(False)
            return combo

        for size in self.sizes:
            display = '{} (доступно: {})'.format(
                size['value'], size['quantity_available']
            )
            combo.addItem(
                display,
                (size['size_id'], size['quantity_available']),
            )
        return combo

    def _make_footer_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        add_button = QPushButton('Добавить в заказ')
        add_button.setMinimumHeight(44)
        add_button.clicked.connect(self._add_to_basket)
        if not self.sizes:
            add_button.setEnabled(False)
        row.addWidget(add_button)

        back_button = QPushButton('Назад')
        back_button.setMinimumHeight(44)
        back_button.setStyleSheet(self._secondary_button_style())
        back_button.clicked.connect(self.reject)
        row.addWidget(back_button)

        return row

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
    # Вспомогательные методы
    # ------------------------------------------------------------------
    def _load_product_pixmap(self) -> QPixmap:
        image_name = self.product.get('image_path')
        if image_name:
            path = os.path.join(PRODUCTS_IMG_DIR, image_name)
            if os.path.exists(path):
                return QPixmap(path)

        placeholder = os.path.join(RESOURCES_DIR, 'picture.png')
        if os.path.exists(placeholder):
            return QPixmap(placeholder)
        return QPixmap()

    def _sync_max_quantity(self):
        data = self.size_combo.currentData()
        if data:
            self.quantity_spin.setMaximum(data[1])
        else:
            self.quantity_spin.setMaximum(0)

    # ------------------------------------------------------------------
    # Добавление в корзину
    # ------------------------------------------------------------------
    def _add_to_basket(self):
        size_data = self.size_combo.currentData()
        if not size_data:
            notify_error(self, 'Выберите доступный размер')
            return

        size_id, available = size_data
        quantity = self.quantity_spin.value()

        if quantity <= 0 or quantity > available:
            notify_error(
                self,
                'Количество должно быть от 1 до {}'.format(available),
            )
            return

        unit_price = calculate_price_with_discount(
            float(self.product['price']), self.discount
        )

        # Если такая позиция уже есть — увеличиваем количество
        for position in self.basket:
            if (position['product_id'] == self.product_id
                    and position['size_id'] == size_id):
                position['quantity'] += quantity
                notify_success(self, 'Количество в заказе увеличено')
                self.accept()
                return

        # Иначе — добавляем новую
        size_text = self.size_combo.currentText().split(' ')[0]
        self.basket.append({
            'product_id': self.product_id,
            'name': self.product['name'],
            'manufacturer': self.product.get('manufacturer', ''),
            'size_id': size_id,
            'size_value': size_text,
            'quantity': quantity,
            'price': unit_price,
        })
        notify_success(self, 'Товар добавлен в заказ')
        self.accept()