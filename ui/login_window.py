"""Диалоговое окно авторизации пользователя по логину"""
import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from config import RESOURCES_DIR, STYLESHEET
from db import select_one
from utils.messages import notify_error


class AuthDialog(QDialog):
    """
    Диалог входа в систему.

    После успешного закрытия через accept() возвращает словарь
    с данными пользователя (см. метод get_profile()).
    """

    LOGO_HEIGHT = 120

    def __init__(self):
        super().__init__()

        # Данные авторизованного пользователя
        self.profile = None

        # Оформление окна
        self.setWindowTitle('Чудо Обувь — Вход')
        self.resize(420, 380)
        self.setStyleSheet(STYLESHEET)
        self._apply_window_icon()

        # Сборка интерфейса
        self._compose_layout()

    # ------------------------------------------------------------------
    # Внешний вид окна
    # ------------------------------------------------------------------
    def _apply_window_icon(self):
        """Ставит иконку приложения, если файл существует."""
        icon_path = os.path.join(RESOURCES_DIR, 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _compose_layout(self):
        """Собирает все элементы диалога."""
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)

        self._add_logo(root)
        self._add_title(root)
        root.addSpacing(20)
        self._add_login_field(root)
        root.addSpacing(20)
        self._add_buttons(root)
        root.addStretch()

    def _add_logo(self, layout: QVBoxLayout):
        """Добавляет логотип в верхнюю часть окна."""
        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if not os.path.exists(logo_path):
            return

        logo_widget = QLabel()
        logo_widget.setPixmap(
            QPixmap(logo_path).scaledToHeight(
                self.LOGO_HEIGHT,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_widget)

    def _add_title(self, layout: QVBoxLayout):
        """Добавляет текстовый заголовок."""
        title = QLabel('Вход в систему')
        title.setStyleSheet(
            'font-size: 20px; font-weight: bold; color: #70B2AF;'
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

    def _add_login_field(self, layout: QVBoxLayout):
        """Добавляет подпись и поле ввода логина."""
        layout.addWidget(QLabel('Логин:'))

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText('Введите логин')
        self.login_edit.returnPressed.connect(self._handle_login)
        layout.addWidget(self.login_edit)

    def _add_buttons(self, layout: QVBoxLayout):
        """Добавляет кнопки входа и гостевого режима."""
        row = QHBoxLayout()

        sign_in_btn = QPushButton('Войти')
        sign_in_btn.clicked.connect(self._handle_login)
        row.addWidget(sign_in_btn)

        guest_btn = QPushButton('Вход для гостя')
        guest_btn.setStyleSheet(self._guest_button_style())
        guest_btn.clicked.connect(self._handle_guest)
        row.addWidget(guest_btn)

        layout.addLayout(row)

    @staticmethod
    def _guest_button_style() -> str:
        """Стиль светлой кнопки для гостевого режима."""
        return (
            'QPushButton {'
            '    background-color: #D2F6E7;'
            '    color: #333;'
            '    border: 1px solid #70B2AF;'
            '    padding: 8px 16px;'
            '    border-radius: 4px;'
            '    font-weight: bold;'
            '}'
            'QPushButton:hover { background-color: #BBEBD7; }'
        )

    # ------------------------------------------------------------------
    # Обработчики событий
    # ------------------------------------------------------------------
    def _handle_login(self):
        """Пытается найти пользователя по введённому логину."""
        entered_login = self.login_edit.text().strip()

        if not entered_login:
            notify_error(self, 'Введите логин')
            return

        user_row = select_one(
            'SELECT u.id, u.last_name, u.first_name, u.middle_name, '
            '       u.login, r.name AS role_name '
            'FROM users u '
            'JOIN roles r ON r.id = u.role_id '
            'WHERE u.login = %s',
            (entered_login,),
        )

        if user_row is None:
            notify_error(
                self,
                'Пользователь с логином «{}» не найден'.format(entered_login),
            )
            return

        self.profile = self._build_profile(user_row)
        self.accept()

    def _handle_guest(self):
        """Закрывает диалог в режиме гостя без авторизации."""
        self.profile = {
            'id': None,
            'login': None,
            'role_name': 'Неавторизованный',
            'full_name': 'Гость',
        }
        self.accept()

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------
    @staticmethod
    def _build_profile(user_row: dict) -> dict:
        """Собирает компактный словарь с данными пользователя."""
        name_parts = (
            user_row['last_name'],
            user_row['first_name'],
            user_row['middle_name'],
        )
        return {
            'id': user_row['id'],
            'login': user_row['login'],
            'role_name': user_row['role_name'],
            'full_name': ' '.join(part for part in name_parts if part),
        }

    def get_profile(self) -> dict:
        """Возвращает данные авторизованного пользователя (или гостя)."""
        return self.profile