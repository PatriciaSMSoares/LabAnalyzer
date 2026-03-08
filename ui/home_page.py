from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QButtonGroup, QScrollArea, QFrame, QMessageBox, QSizePolicy,
    QGridLayout, QGroupBox, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.file_loader import FileLoader, FileParseError
from labanalyzer.core.data_models import DataSet
from labanalyzer.ui.widgets.file_selector import FileSelectorWidget
from labanalyzer.ui.widgets.mass_file_widget import MassFileWidget
from labanalyzer.utils.color_cycle import ColorCycle


class MeasurementTile(QPushButton):
    """Tile button for measurement type selection."""

    def __init__(self, measurement_cls, parent=None):
        super().__init__(parent)
        self._measurement_cls = measurement_cls
        self.setCheckable(True)
        self.setMinimumSize(120, 90)
        self.setMaximumSize(160, 120)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        label = measurement_cls.display_name
        self.setText(label)

        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.setFont(font)

        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 2px solid #D0D7E3;
                border-radius: 8px;
                padding: 8px;
                color: #1A1A2E;
            }
            QPushButton:hover {
                border-color: #2E75B6;
                background-color: #EEF2F7;
            }
            QPushButton:checked {
                border-color: #2E75B6;
                background-color: #DDEAF5;
                color: #2E75B6;
            }
        """)

    @property
    def measurement_cls(self):
        return self._measurement_cls


class HomePage(QWidget):
    """Home page with measurement selection and file management."""
    create_tab_requested = pyqtSignal(object, list, list)  # measurement_cls, datasets, mass_entries

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_measurement = None
        self._files: list[Path] = []
        self._mass_entries = []
        self._tile_group = QButtonGroup()
        self._tile_group.setExclusive(True)
        self._tiles: list[MeasurementTile] = []
        self._setup_ui()
        self._load_measurements()

    def _setup_ui(self):
        # Outer layout holds a scroll area that fills the whole page
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scroll area wraps all content so nothing gets squished
        page_scroll = QScrollArea()
        page_scroll.setWidgetResizable(True)
        page_scroll.setFrameShape(QFrame.Shape.NoFrame)
        page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(page_scroll)

        # Inner content widget
        content = QWidget()
        page_scroll.setWidget(content)
        inner = QVBoxLayout(content)
        inner.setContentsMargins(20, 20, 20, 20)
        inner.setSpacing(16)

        # Header
        header = QLabel('LabAnalyzer')
        header.setObjectName('heading')
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(header)

        subtitle = QLabel('Select a measurement type, load your data files, and create an analysis tab.')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet('color: #595959;')
        inner.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet('color: #D0D7E3;')
        inner.addWidget(sep)

        # Section A: Measurement tiles
        section_a = QGroupBox('Measurement Type')
        section_a_layout = QVBoxLayout(section_a)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(160)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._tiles_container = QWidget()
        self._tiles_layout = QHBoxLayout(self._tiles_container)
        self._tiles_layout.setContentsMargins(4, 4, 4, 4)
        self._tiles_layout.setSpacing(8)
        self._tiles_layout.addStretch()

        scroll.setWidget(self._tiles_container)
        section_a_layout.addWidget(scroll)
        inner.addWidget(section_a)

        # Section B: File selector
        section_b = QGroupBox('Data Files')
        section_b_layout = QVBoxLayout(section_b)

        self._file_selector = FileSelectorWidget()
        self._file_selector.setMinimumHeight(220)
        self._file_selector.files_changed.connect(self._on_files_changed)
        section_b_layout.addWidget(self._file_selector)
        inner.addWidget(section_b)

        # Mass file widget (shown conditionally)
        self._mass_section = QGroupBox('Sample Mass File')
        mass_layout = QVBoxLayout(self._mass_section)
        self._mass_widget = MassFileWidget()
        self._mass_widget.mass_data_changed.connect(self._on_mass_changed)
        mass_layout.addWidget(self._mass_widget)
        self._mass_section.setVisible(False)
        inner.addWidget(self._mass_section)

        # Section C: Action bar
        self._create_btn = QPushButton('Create Analysis Tab')
        self._create_btn.setFixedHeight(44)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._create_btn.setFont(font)
        self._create_btn.clicked.connect(self._create_tab)
        inner.addWidget(self._create_btn)

        inner.addStretch()

    def _load_measurements(self):
        """Load all registered measurements and create tiles."""
        measurements = MeasurementRegistry.all_measurements()
        for m_cls in measurements:
            tile = MeasurementTile(m_cls)
            self._tile_group.addButton(tile)
            self._tiles.append(tile)
            # Insert before the stretch
            self._tiles_layout.insertWidget(self._tiles_layout.count() - 1, tile)
            tile.toggled.connect(lambda checked, cls=m_cls: self._on_tile_toggled(checked, cls))

        if measurements:
            self._tiles[0].setChecked(True)

    def _on_tile_toggled(self, checked: bool, measurement_cls):
        if checked:
            self._selected_measurement = measurement_cls
            self._file_selector.set_extensions(measurement_cls.supported_extensions)
            self._mass_section.setVisible(measurement_cls.requires_mass_file)

    def _on_files_changed(self, files: list):
        self._files = files

    def _on_mass_changed(self, entries: list):
        self._mass_entries = entries

    def _create_tab(self):
        """Validate and emit create_tab_requested signal."""
        if self._selected_measurement is None:
            QMessageBox.warning(self, 'No Measurement', 'Please select a measurement type.')
            return

        if not self._files:
            QMessageBox.warning(self, 'No Files', 'Please add at least one data file.')
            return

        if self._selected_measurement.requires_mass_file and not self._mass_entries:
            reply = QMessageBox.question(
                self, 'Mass File Missing',
                f'{self._selected_measurement.display_name} works best with a mass file.\n'
                'Continue without mass data?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Load files
        loader = FileLoader()
        datasets = []
        failed = []
        color_cycle = ColorCycle()

        for path in self._files:
            try:
                df = loader.load(path)
                ds = DataSet(
                    file_path=path,
                    display_name=path.stem,
                    raw_data=df,
                    group_name=path.parent.name,
                )
                datasets.append(ds)
            except FileParseError as e:
                failed.append(f'{path.name}: {e}')
            except Exception as e:
                failed.append(f'{path.name}: Unexpected error: {e}')

        if failed:
            msg = 'Failed to load:\n' + '\n'.join(failed)
            QMessageBox.warning(self, 'Load Errors', msg)

        if not datasets:
            QMessageBox.critical(self, 'Error', 'No files could be loaded.')
            return

        color_cycle.assign_colors(datasets)
        self.create_tab_requested.emit(self._selected_measurement, datasets, self._mass_entries)
