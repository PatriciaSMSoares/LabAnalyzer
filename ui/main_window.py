import time
import traceback
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QStatusBar,
    QLabel, QMessageBox, QFileDialog, QWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont

from labanalyzer.config import AppConfig
from labanalyzer.ui.home_page import HomePage
from labanalyzer.ui.analysis_tab import AnalysisTab


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._tab_count = 0
        self.setWindowTitle('LabAnalyzer')
        self.setMinimumSize(1100, 700)
        self._setup_ui()
        self._setup_menus()
        self._setup_statusbar()
        self._restore_geometry()

    def _setup_ui(self):
        # Central tab widget
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self.setCentralWidget(self._tabs)

        # Home tab (always present, not closeable)
        self._home = HomePage()
        self._home.create_tab_requested.connect(self._create_analysis_tab)
        self._tabs.addTab(self._home, 'Home')
        self._tabs.tabBar().setTabButton(0, self._tabs.tabBar().ButtonPosition.RightSide, None)

    def _setup_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        recent_menu = file_menu.addMenu('Open Recent')
        self._recent_menu = recent_menu
        self._populate_recent_menu()

        export_all_action = QAction('Export All Plots...', self)
        export_all_action.triggered.connect(self._export_all)
        file_menu.addAction(export_all_action)

        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        theme_menu = view_menu.addMenu('Theme')
        light_action = QAction('Light', self)
        light_action.triggered.connect(lambda: self._set_theme('light'))
        theme_menu.addAction(light_action)
        dark_action = QAction('Dark', self)
        dark_action.triggered.connect(lambda: self._set_theme('dark'))
        theme_menu.addAction(dark_action)

        font_menu = view_menu.addMenu('Font Size')
        for size in [9, 10, 11, 12, 14]:
            action = QAction(f'{size}pt', self)
            action.triggered.connect(lambda checked, s=size: self._set_font_size(s))
            font_menu.addAction(action)

        reset_action = QAction('Reset Layout', self)
        reset_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_action)

        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        docs_action = QAction('Documentation', self)
        docs_action.triggered.connect(self._show_docs)
        help_menu.addAction(docs_action)

    def _setup_statusbar(self):
        self._statusbar = self.statusBar()

        self._status_files_label = QLabel('Ready')
        self._statusbar.addWidget(self._status_files_label)

        self._statusbar.addPermanentWidget(QLabel(' | '))

        self._status_render_label = QLabel('Last render: —')
        self._statusbar.addPermanentWidget(self._status_render_label)

        self._statusbar.addPermanentWidget(QLabel(' | '))

        self._status_mem_label = QLabel('Mem: —')
        self._statusbar.addPermanentWidget(self._status_mem_label)

        # Memory usage timer
        self._mem_timer = QTimer()
        self._mem_timer.timeout.connect(self._update_memory)
        self._mem_timer.start(5000)

    def _update_memory(self):
        try:
            import psutil
            import os
            proc = psutil.Process(os.getpid())
            mem_mb = proc.memory_info().rss / 1024 / 1024
            self._status_mem_label.setText(f'Mem: {mem_mb:.0f} MB')
            if mem_mb > 500:
                self._status_mem_label.setStyleSheet('color: #E68000; font-weight: bold;')
            else:
                self._status_mem_label.setStyleSheet('')
        except ImportError:
            self._status_mem_label.setText('Mem: N/A')

    def create_analysis_tab(self, session_config: dict):
        """Create a new analysis tab from session config dict."""
        measurement_cls = session_config.get('measurement_cls')
        datasets = session_config.get('datasets', [])
        if measurement_cls and datasets:
            self._create_analysis_tab(measurement_cls, datasets, [])

    def _create_analysis_tab(self, measurement_cls, datasets: list, mass_entries: list):
        """Create and add an analysis tab."""
        self._tab_count += 1
        n_files = len(datasets)
        type_name = measurement_cls.display_name
        title = f'{type_name} — {n_files} files'
        if len(title) > 30:
            title = title[:27] + '...'

        tab = AnalysisTab(datasets, measurement_cls)
        tab.render_complete.connect(
            lambda elapsed: self._status_render_label.setText(f'Last render: {elapsed*1000:.0f}ms')
        )
        tab.status_message.connect(self._status_files_label.setText)
        tab.close_requested.connect(lambda: self._close_tab_by_widget(tab))

        idx = self._tabs.addTab(tab, title)
        self._tabs.setCurrentIndex(idx)
        self._status_files_label.setText(f'{n_files} files loaded')

    def _close_tab_by_widget(self, widget: QWidget):
        idx = self._tabs.indexOf(widget)
        if idx > 0:
            self._tabs.removeTab(idx)

    def _on_tab_close_requested(self, idx: int):
        if idx == 0:
            return  # don't close home tab
        self._tabs.removeTab(idx)

    def _populate_recent_menu(self):
        self._recent_menu.clear()
        if not self._config.recent_dirs:
            self._recent_menu.addAction('(empty)').setEnabled(False)
            return
        for path in self._config.recent_dirs[:10]:
            action = QAction(path, self)
            action.triggered.connect(lambda checked, p=path: self._open_recent(p))
            self._recent_menu.addAction(action)

    def _open_recent(self, path: str):
        from labanalyzer.ui.home_page import HomePage
        # Switch to home and set folder
        self._tabs.setCurrentIndex(0)
        # Could pre-populate file selector — for now just show home
        self._status_files_label.setText(f'Open recent: {path}')

    def _export_all(self):
        folder = QFileDialog.getExistingDirectory(self, 'Export All Plots To...')
        if not folder:
            return
        folder_path = Path(folder)
        count = 0
        for i in range(1, self._tabs.count()):
            tab = self._tabs.widget(i)
            if isinstance(tab, AnalysisTab):
                filename = f'plot_{i:02d}_{self._tabs.tabText(i)[:20]}.png'
                filename = filename.replace(' ', '_').replace('/', '_')
                try:
                    tab._plot_canvas.figure.savefig(
                        folder_path / filename, dpi=150, bbox_inches='tight'
                    )
                    count += 1
                except Exception:
                    pass
        QMessageBox.information(self, 'Export Complete', f'Exported {count} plots to {folder}')

    def _set_theme(self, theme: str):
        from labanalyzer.theme import get_theme
        from PyQt6.QtWidgets import QApplication
        self._config.theme = theme
        self._config.save()
        app = QApplication.instance()
        app.setStyleSheet(get_theme(theme))

    def _set_font_size(self, size: int):
        from PyQt6.QtWidgets import QApplication
        self._config.font_size = size
        self._config.save()
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(size)
        app.setFont(font)

    def _reset_layout(self):
        self.resize(1100, 700)
        self.move(100, 100)

    def _show_about(self):
        QMessageBox.about(
            self,
            'About LabAnalyzer',
            '<b>LabAnalyzer</b> v0.1.0<br><br>'
            'Desktop GUI for managing, processing, and visualizing experimental measurement data.<br><br>'
            'Built with Python, PyQt6, and Matplotlib.',
        )

    def _show_docs(self):
        QMessageBox.information(
            self,
            'Documentation',
            'Documentation is available in the README.md file in the project directory.',
        )

    def _restore_geometry(self):
        geom = self._config.window_geometry
        if geom:
            try:
                self.resize(geom.get('width', 1200), geom.get('height', 800))
                self.move(geom.get('x', 100), geom.get('y', 100))
            except Exception:
                pass

    def closeEvent(self, event):
        # Save geometry
        geom = self.geometry()
        self._config.window_geometry = {
            'x': geom.x(),
            'y': geom.y(),
            'width': geom.width(),
            'height': geom.height(),
        }
        self._config.save()
        event.accept()
