import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from labanalyzer.config import AppConfig
from labanalyzer.theme import get_theme


def create_app(config: AppConfig | None = None) -> tuple:
    """Create and configure the QApplication."""
    app = QApplication.instance() or QApplication(sys.argv)

    if config is None:
        config = AppConfig.load()

    # Set font
    font = QFont('Segoe UI', config.font_size)
    app.setFont(font)

    # Apply theme
    app.setStyleSheet(get_theme(config.theme))

    app.setApplicationName('LabAnalyzer')
    app.setApplicationVersion('0.1.0')
    app.setOrganizationName('LabAnalyzer')

    return app, config
