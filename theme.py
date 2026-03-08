LIGHT_THEME = """
QWidget {
    background-color: #F5F7FA;
    color: #1A1A2E;
    font-size: 11pt;
    font-family: "Segoe UI", Arial, sans-serif;
}

QMainWindow {
    background-color: #F5F7FA;
}

QTabWidget::pane {
    border: 1px solid #D0D7E3;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #EEF2F7;
    color: #595959;
    padding: 6px 14px;
    border: 1px solid #D0D7E3;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1A1A2E;
    border-bottom: 1px solid #FFFFFF;
}

QTabBar::tab:hover {
    background-color: #DDEAF5;
}

QPushButton {
    background-color: #2E75B6;
    color: #FFFFFF;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1F4E79;
}

QPushButton:pressed {
    background-color: #163a5c;
}

QPushButton:disabled {
    background-color: #B0B8C4;
    color: #FFFFFF;
}

QPushButton#secondary {
    background-color: #EEF2F7;
    color: #2E75B6;
    border: 1px solid #D0D7E3;
}

QPushButton#secondary:hover {
    background-color: #D0D7E3;
}

QPushButton#danger {
    background-color: #C5504A;
    color: #FFFFFF;
}

QPushButton#danger:hover {
    background-color: #a03e39;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    border-radius: 4px;
    padding: 4px 8px;
    color: #1A1A2E;
    selection-background-color: #2E75B6;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #2E75B6;
}

QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    border-radius: 4px;
    padding: 4px 8px;
    color: #1A1A2E;
    min-width: 80px;
}

QComboBox:focus {
    border-color: #2E75B6;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    selection-background-color: #2E75B6;
    selection-color: #FFFFFF;
}

QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    border-radius: 4px;
    padding: 4px 8px;
    color: #1A1A2E;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #2E75B6;
}

QCheckBox {
    spacing: 6px;
    color: #1A1A2E;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #D0D7E3;
    border-radius: 3px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #2E75B6;
    border-color: #2E75B6;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #F5F7FA;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #B0B8C4;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #2E75B6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #F5F7FA;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #B0B8C4;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #2E75B6;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTreeWidget {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    border-radius: 4px;
    alternate-background-color: #F5F7FA;
}

QTreeWidget::item {
    padding: 3px 0;
    color: #1A1A2E;
}

QTreeWidget::item:selected {
    background-color: #2E75B6;
    color: #FFFFFF;
}

QTreeWidget::item:hover {
    background-color: #EEF2F7;
}

QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    border-radius: 4px;
}

QListWidget::item {
    padding: 4px;
    color: #1A1A2E;
}

QListWidget::item:selected {
    background-color: #2E75B6;
    color: #FFFFFF;
}

QSplitter::handle {
    background-color: #D0D7E3;
    width: 2px;
    height: 2px;
}

QGroupBox {
    border: 1px solid #D0D7E3;
    border-radius: 6px;
    margin-top: 12px;
    padding: 8px;
    color: #1A1A2E;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    background-color: #F5F7FA;
}

QLabel {
    color: #1A1A2E;
    background-color: transparent;
}

QLabel#heading {
    font-size: 14pt;
    font-weight: 700;
    color: #1A1A2E;
}

QLabel#subheading {
    font-size: 12pt;
    font-weight: 600;
    color: #2E75B6;
}

QStatusBar {
    background-color: #EEF2F7;
    border-top: 1px solid #D0D7E3;
    color: #595959;
}

QMenuBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #D0D7E3;
    color: #1A1A2E;
}

QMenuBar::item:selected {
    background-color: #EEF2F7;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #D0D7E3;
    color: #1A1A2E;
}

QMenu::item:selected {
    background-color: #2E75B6;
    color: #FFFFFF;
}

QToolBar {
    background-color: #F5F7FA;
    border-bottom: 1px solid #D0D7E3;
    spacing: 4px;
}

QFrame#separator {
    background-color: #D0D7E3;
    max-height: 1px;
}

QWidget#tile_button {
    background-color: #FFFFFF;
    border: 2px solid #D0D7E3;
    border-radius: 8px;
}

QWidget#tile_button:hover {
    border-color: #2E75B6;
    background-color: #EEF2F7;
}

QWidget#tile_button[selected=true] {
    border-color: #2E75B6;
    background-color: #DDEAF5;
}

QWidget#error_banner {
    background-color: #FDECEA;
    border: 1px solid #C5504A;
    border-radius: 4px;
    padding: 8px;
}

QWidget#success_banner {
    background-color: #E8F5E9;
    border: 1px solid #2D8A4E;
    border-radius: 4px;
    padding: 8px;
}
"""

DARK_THEME = """
QWidget {
    background-color: #1E1E2E;
    color: #CDD6F4;
    font-size: 11pt;
    font-family: "Segoe UI", Arial, sans-serif;
}

QMainWindow {
    background-color: #1E1E2E;
}

QTabWidget::pane {
    border: 1px solid #45475A;
    background-color: #181825;
}

QTabBar::tab {
    background-color: #313244;
    color: #A6ADC8;
    padding: 6px 14px;
    border: 1px solid #45475A;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #181825;
    color: #CDD6F4;
    border-bottom: 1px solid #181825;
}

QTabBar::tab:hover {
    background-color: #45475A;
}

QPushButton {
    background-color: #89B4FA;
    color: #1E1E2E;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #B4BEFE;
}

QPushButton:pressed {
    background-color: #74C7EC;
}

QPushButton:disabled {
    background-color: #45475A;
    color: #6C7086;
}

QPushButton#secondary {
    background-color: #313244;
    color: #89B4FA;
    border: 1px solid #45475A;
}

QPushButton#secondary:hover {
    background-color: #45475A;
}

QPushButton#danger {
    background-color: #F38BA8;
    color: #1E1E2E;
}

QPushButton#danger:hover {
    background-color: #EBA0AC;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 4px;
    padding: 4px 8px;
    color: #CDD6F4;
    selection-background-color: #89B4FA;
    selection-color: #1E1E2E;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #89B4FA;
}

QComboBox {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 4px;
    padding: 4px 8px;
    color: #CDD6F4;
    min-width: 80px;
}

QComboBox:focus {
    border-color: #89B4FA;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475A;
    selection-background-color: #89B4FA;
    selection-color: #1E1E2E;
}

QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 4px;
    padding: 4px 8px;
    color: #CDD6F4;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #89B4FA;
}

QCheckBox {
    spacing: 6px;
    color: #CDD6F4;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #45475A;
    border-radius: 3px;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89B4FA;
    border-color: #89B4FA;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #1E1E2E;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #45475A;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #89B4FA;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1E1E2E;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #45475A;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #89B4FA;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTreeWidget {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 4px;
    alternate-background-color: #1E1E2E;
}

QTreeWidget::item {
    padding: 3px 0;
    color: #CDD6F4;
}

QTreeWidget::item:selected {
    background-color: #89B4FA;
    color: #1E1E2E;
}

QTreeWidget::item:hover {
    background-color: #45475A;
}

QListWidget {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 4px;
}

QListWidget::item {
    padding: 4px;
    color: #CDD6F4;
}

QListWidget::item:selected {
    background-color: #89B4FA;
    color: #1E1E2E;
}

QSplitter::handle {
    background-color: #45475A;
    width: 2px;
    height: 2px;
}

QGroupBox {
    border: 1px solid #45475A;
    border-radius: 6px;
    margin-top: 12px;
    padding: 8px;
    color: #CDD6F4;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    background-color: #1E1E2E;
}

QLabel {
    color: #CDD6F4;
    background-color: transparent;
}

QLabel#heading {
    font-size: 14pt;
    font-weight: 700;
    color: #CDD6F4;
}

QLabel#subheading {
    font-size: 12pt;
    font-weight: 600;
    color: #89B4FA;
}

QStatusBar {
    background-color: #181825;
    border-top: 1px solid #45475A;
    color: #A6ADC8;
}

QMenuBar {
    background-color: #181825;
    border-bottom: 1px solid #45475A;
    color: #CDD6F4;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenu {
    background-color: #1E1E2E;
    border: 1px solid #45475A;
    color: #CDD6F4;
}

QMenu::item:selected {
    background-color: #89B4FA;
    color: #1E1E2E;
}

QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #45475A;
    spacing: 4px;
}

QFrame#separator {
    background-color: #45475A;
    max-height: 1px;
}

QWidget#tile_button {
    background-color: #313244;
    border: 2px solid #45475A;
    border-radius: 8px;
}

QWidget#tile_button:hover {
    border-color: #89B4FA;
    background-color: #45475A;
}

QWidget#tile_button[selected=true] {
    border-color: #89B4FA;
    background-color: #1e3a5f;
}

QWidget#error_banner {
    background-color: #3b1219;
    border: 1px solid #F38BA8;
    border-radius: 4px;
    padding: 8px;
}

QWidget#success_banner {
    background-color: #122b1a;
    border: 1px solid #A6E3A1;
    border-radius: 4px;
    padding: 8px;
}
"""


def get_theme(name: str) -> str:
    if name == 'dark':
        return DARK_THEME
    return LIGHT_THEME
