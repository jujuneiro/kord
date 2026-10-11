"""Диалоговые окна обратной связи для пользователя"""
from PyQt6.QtWidgets import QMessageBox


# ======================================================================
# Внутренние помощники
# ======================================================================
def _show_message(parent, text: str, title: str, icon) -> None:
    """
    Универсальный конструктор модального диалога.

    Используется остальными функциями модуля для единообразия
    отображения сообщений (иконка + заголовок + текст).
    """
    dialog = QMessageBox(parent)
    dialog.setIcon(icon)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    dialog.exec()


# ======================================================================
# Публичные функции
# ======================================================================
def notify_error(parent, text: str, title: str = 'Ошибка') -> None:
    """Показывает критическую ошибку."""
    _show_message(parent, text, title, QMessageBox.Icon.Critical)


def notify_warning(parent, text: str, title: str = 'Предупреждение') -> None:
    """Показывает предупреждение."""
    _show_message(parent, text, title, QMessageBox.Icon.Warning)


def notify_success(parent, text: str, title: str = 'Информация') -> None:
    """Показывает информационное сообщение."""
    _show_message(parent, text, title, QMessageBox.Icon.Information)


def ask_confirm(parent, text: str, title: str = 'Подтверждение') -> bool:
    """
    Запрашивает у пользователя подтверждение действия.

    Возвращает True, если пользователь нажал «Да», иначе False.
    """
    answer = QMessageBox.question(
        parent,
        title,
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return answer == QMessageBox.StandardButton.Yes