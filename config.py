"""Конфигурация приложения Чудо Обувь"""
import os

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
PRODUCTS_IMG_DIR = os.path.join(RESOURCES_DIR, 'products')

# БД
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'chudo_obuv',
    'user': 'postgres',
    'password': 'ТВОЙ_ПАРОЛЬ',   # ← замени на свой!
}

# ======================================================================
# Палитра (по Приложению 3 — НЕ менять значения!)
# ======================================================================
COLOR_BG_MAIN = '#FFFFFF'
COLOR_BG_SECONDARY = '#D2F6E7'
COLOR_ACCENT = '#70B2AF'
COLOR_ACCENT_DARK = '#5a9a97'
COLOR_LOW_STOCK = '#ff8080'
COLOR_TEXT = '#2c3e50'
COLOR_TEXT_MUTED = '#95a5a6'
COLOR_BORDER = '#d0d8dc'
COLOR_WHITE = '#ffffff'

FONT_FAMILY = 'Calibri'

# ======================================================================
# Размеры и отступы
# ======================================================================
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
LOGO_HEIGHT_HEADER = 80
LOGO_HEIGHT_DIALOG = 140
CARD_IMAGE_SIZE = 170
CARD_BORDER_RADIUS = 12
BUTTON_BORDER_RADIUS = 8
BUTTON_PADDING = '10px 22px'
INPUT_PADDING = '10px 14px'
CARD_MARGIN = 16
CARDS_SPACING = 12

# ======================================================================
# Общий стиль приложения
# ======================================================================
STYLESHEET = f"""
QWidget {{
    background-color: {COLOR_BG_MAIN};
    font-family: '{FONT_FAMILY}';
    font-size: 13px;
    color: {COLOR_TEXT};
}}

QMainWindow, QDialog {{
    background-color: {COLOR_BG_MAIN};
}}

QPushButton {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_WHITE};
    border: none;
    padding: {BUTTON_PADDING};
    border-radius: {BUTTON_BORDER_RADIUS}px;
    font-weight: bold;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {COLOR_ACCENT_DARK};
}}
QPushButton:pressed {{
    background-color: #4a8582;
}}
QPushButton:disabled {{
    background-color: #cccccc;
    color: #888888;
}}

QLineEdit, QSpinBox, QDateEdit {{
    background-color: {COLOR_BG_SECONDARY};
    border: 1px solid {COLOR_ACCENT};
    border-radius: {BUTTON_BORDER_RADIUS}px;
    padding: {INPUT_PADDING};
    font-size: 13px;
    color: {COLOR_TEXT};
    selection-background-color: {COLOR_ACCENT};
    selection-color: {COLOR_WHITE};
}}
QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {{
    border: 2px solid {COLOR_ACCENT};
    background-color: #eafcf4;
}}
QLineEdit:disabled, QSpinBox:disabled, QDateEdit:disabled {{
    background-color: #f5f5f5;
    color: #888888;
    border-color: #cccccc;
}}

QComboBox {{
    background-color: {COLOR_BG_SECONDARY};
    border: 1px solid {COLOR_ACCENT};
    border-radius: {BUTTON_BORDER_RADIUS}px;
    padding: 8px 12px;
    font-size: 13px;
    color: {COLOR_TEXT};
    min-width: 100px;
}}
QComboBox:hover {{
    border-color: {COLOR_ACCENT_DARK};
}}
QComboBox:focus {{
    border: 2px solid {COLOR_ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLOR_ACCENT};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_ACCENT};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {COLOR_BG_SECONDARY};
    selection-color: {COLOR_TEXT};
    outline: none;
}}

QTextEdit {{
    background-color: {COLOR_BG_SECONDARY};
    border: 1px solid {COLOR_ACCENT};
    border-radius: {BUTTON_BORDER_RADIUS}px;
    padding: 8px 12px;
    font-size: 13px;
    color: {COLOR_TEXT};
}}
QTextEdit:focus {{
    border: 2px solid {COLOR_ACCENT};
}}

QTableWidget {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_BORDER};
    border-radius: {BUTTON_BORDER_RADIUS}px;
    gridline-color: #eaeef0;
    font-size: 13px;
    color: {COLOR_TEXT};
    selection-background-color: {COLOR_BG_SECONDARY};
    selection-color: {COLOR_TEXT};
    alternate-background-color: #fbfdfc;
}}
QTableWidget::item {{
    padding: 6px 10px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: {COLOR_BG_SECONDARY};
    color: {COLOR_TEXT};
}}
QHeaderView::section {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_WHITE};
    padding: 10px 8px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}}
QHeaderView::section:first {{
    border-top-left-radius: {BUTTON_BORDER_RADIUS}px;
}}
QHeaderView::section:last {{
    border-top-right-radius: {BUTTON_BORDER_RADIUS}px;
}}

QLabel {{
    color: {COLOR_TEXT};
    background: transparent;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_ACCENT};
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT_DARK};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 12px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {COLOR_ACCENT};
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLOR_BG_SECONDARY};
    border: 1px solid {COLOR_ACCENT};
    width: 20px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLOR_ACCENT};
}}
"""