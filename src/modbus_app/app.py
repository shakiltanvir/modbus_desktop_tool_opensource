from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .branding import APP_NAME, APP_STYLE_SHEET, ORGANIZATION_NAME, create_app_icon
from .ui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setWindowIcon(create_app_icon())
    app.setStyleSheet(APP_STYLE_SHEET)
    window = MainWindow()
    window.show()
    return app.exec()
