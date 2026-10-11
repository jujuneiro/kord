"""Точка входа приложения Чудо Обувь"""
import sys
from PyQt6.QtWidgets import QApplication, QDialog

from config import STYLESHEET
from ui.login_window import AuthDialog
from ui.main_window import CatalogWindow


def main():
    """Запуск приложения: авторизация → каталог."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLESHEET)

    # 1. Диалог авторизации
    login = AuthDialog()
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    # 2. Главное окно каталога
    current_user = login.get_profile()
    window = CatalogWindow(current_user=current_user)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()