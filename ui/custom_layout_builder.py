from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpinBox, QScrollArea, QWidget, QGridLayout, QFrame,
    QListWidget, QListWidgetItem, QComboBox, QSplitter,
    QFileDialog, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json
from pathlib import Path
from math import ceil
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from labanalyzer.core.data_models import CustomLayoutConfig, CellConfig, PlotConfig


class CellConfigDialog(QDialog):
    """Popover dialog for configuring a single grid cell."""

    def __init__(self, analyses: list, datasets: list,
                 current_analysis_id: str = '',
                 current_ds_ids: list | None = None,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configure Cell')
        self.setMinimumWidth(320)
        self._analyses = analyses
        self._datasets = datasets
        self._current_ds_ids = set(current_ds_ids or [])

        layout = QVBoxLayout(self)

        # Analysis type
        layout.addWidget(QLabel('Analysis Type:'))
        self._analysis_combo = QComboBox()
        self._analysis_combo.addItem('(empty)', '')
        for a in analyses:
            self._analysis_combo.addItem(a.display_name, a.analysis_id)
        if current_analysis_id:
            idx = self._analysis_combo.findData(current_analysis_id)
            if idx >= 0:
                self._analysis_combo.setCurrentIndex(idx)
        layout.addWidget(self._analysis_combo)

        # Dataset selection
        layout.addWidget(QLabel('Show datasets (leave all unchecked = show all visible):'))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(180)
        ds_widget = QWidget()
        ds_layout = QVBoxLayout(ds_widget)
        ds_layout.setContentsMargins(4, 4, 4, 4)
        ds_layout.setSpacing(2)
        self._ds_checks: list[tuple[QCheckBox, str]] = []
        for ds in datasets:
            cb = QCheckBox(ds.display_name)
            ds_id = str(ds.file_path)
            cb.setChecked(ds_id in self._current_ds_ids)
            ds_layout.addWidget(cb)
            self._ds_checks.append((cb, ds_id))
        ds_layout.addStretch()
        scroll.setWidget(ds_widget)
        layout.addWidget(scroll)

        # Buttons
        btn_row = QHBoxLayout()
        ok_btn = QPushButton('OK')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setObjectName('secondary')
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def get_analysis_id(self) -> str:
        return self._analysis_combo.currentData() or ''

    def get_analysis_display_name(self) -> str:
        return self._analysis_combo.currentText()

    def get_selected_ds_ids(self) -> list[str]:
        return [ds_id for cb, ds_id in self._ds_checks if cb.isChecked()]


class CellSlot(QFrame):
    """A single cell in the custom layout grid."""
    clicked = pyqtSignal(int, int)  # row, col

    def __init__(self, row: int, col: int, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self._analysis_id = ''
        self._label = ''
        self._data_source_ids: list[str] = []
        self.setFrameShape(QFrame.Shape.Box)
        self.setMinimumSize(120, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(filled=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self._label_widget = QLabel('Empty\n(click to configure)')
        self._label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_widget.setWordWrap(True)
        font = QFont()
        font.setPointSize(8)
        self._label_widget.setFont(font)
        layout.addWidget(self._label_widget)

        self._ds_badge = QLabel('')
        self._ds_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        small = QFont()
        small.setPointSize(7)
        self._ds_badge.setFont(small)
        self._ds_badge.setStyleSheet('color: #595959;')
        layout.addWidget(self._ds_badge)

    def _apply_style(self, filled: bool):
        if filled:
            self.setStyleSheet(
                'QFrame { background: #DDEAF5; border: 2px solid #2E75B6; border-radius: 4px; }'
            )
        else:
            self.setStyleSheet(
                'QFrame { background: white; border: 2px dashed #D0D7E3; border-radius: 4px; }'
                'QFrame:hover { border-color: #2E75B6; background: #EEF2F7; }'
            )

    def set_analysis(self, analysis_id: str, display_name: str,
                     data_source_ids: list[str] | None = None):
        self._analysis_id = analysis_id
        self._label = display_name
        self._data_source_ids = data_source_ids or []
        self._label_widget.setText(display_name or 'Empty\n(click to configure)')
        n = len(self._data_source_ids)
        self._ds_badge.setText(f'{n} file(s) selected' if n else 'all visible files')
        self._apply_style(filled=bool(analysis_id))

    def get_analysis_id(self) -> str:
        return self._analysis_id

    def get_data_source_ids(self) -> list[str]:
        return self._data_source_ids

    def clear(self):
        self.set_analysis('', '', [])

    def mousePressEvent(self, event):
        self.clicked.emit(self.row, self.col)


class CustomLayoutBuilder(QDialog):
    """Modal dialog for building custom multi-panel layouts."""

    def __init__(self, datasets: list, analyses: list, parent=None):
        super().__init__(parent)
        self._datasets = datasets
        self._analyses = analyses
        self._cells: dict[tuple, CellSlot] = {}
        self._grid_rows = 2
        self._grid_cols = 2
        self._figure = Figure(figsize=(8, 4), dpi=80)
        self.setWindowTitle('Custom Layout Builder')
        self.setMinimumSize(900, 640)
        self._setup_ui()
        self._rebuild_grid()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Top bar
        top = QHBoxLayout()
        top.addWidget(QLabel('Rows:'))
        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 6)
        self._rows_spin.setValue(2)
        self._rows_spin.valueChanged.connect(self._on_grid_changed)
        top.addWidget(self._rows_spin)

        top.addWidget(QLabel('Cols:'))
        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 6)
        self._cols_spin.setValue(2)
        self._cols_spin.valueChanged.connect(self._on_grid_changed)
        top.addWidget(self._cols_spin)

        top.addStretch()

        clear_btn = QPushButton('Clear All')
        clear_btn.setObjectName('secondary')
        clear_btn.clicked.connect(self._clear_all)
        top.addWidget(clear_btn)

        save_btn = QPushButton('Save Preset...')
        save_btn.setObjectName('secondary')
        save_btn.clicked.connect(self._save_preset)
        top.addWidget(save_btn)

        load_btn = QPushButton('Load Preset...')
        load_btn.setObjectName('secondary')
        load_btn.clicked.connect(self._load_preset)
        top.addWidget(load_btn)

        cancel_btn = QPushButton('Cancel')
        cancel_btn.setObjectName('secondary')
        cancel_btn.clicked.connect(self.reject)
        top.addWidget(cancel_btn)

        apply_btn = QPushButton('Apply')
        apply_btn.clicked.connect(self._apply)
        top.addWidget(apply_btn)

        layout.addLayout(top)

        # Helper label
        hint = QLabel('Click any cell to assign an analysis and choose which files to display in it.')
        hint.setStyleSheet('color: #595959; font-size: 11px;')
        layout.addWidget(hint)

        # Main splitter: palette | grid
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: analysis palette
        palette_widget = QWidget()
        palette_layout = QVBoxLayout(palette_widget)
        palette_layout.addWidget(QLabel('Analysis Types:'))
        self._palette_list = QListWidget()
        for a in self._analyses:
            item = QListWidgetItem(a.display_name)
            item.setData(Qt.ItemDataRole.UserRole, a.analysis_id)
            self._palette_list.addItem(item)
        palette_layout.addWidget(self._palette_list)
        palette_widget.setMaximumWidth(200)
        splitter.addWidget(palette_widget)

        # Center: grid canvas
        grid_container = QWidget()
        self._grid_layout = QGridLayout(grid_container)
        self._grid_layout.setSpacing(6)
        scroll = QScrollArea()
        scroll.setWidget(grid_container)
        scroll.setWidgetResizable(True)
        splitter.addWidget(scroll)
        self._grid_container = grid_container

        layout.addWidget(splitter, 1)

        # Preview
        layout.addWidget(QLabel('Preview (structure only):'))
        self._preview_canvas = FigureCanvasQTAgg(self._figure)
        self._preview_canvas.setMaximumHeight(160)
        layout.addWidget(self._preview_canvas)

    def _on_grid_changed(self):
        self._grid_rows = self._rows_spin.value()
        self._grid_cols = self._cols_spin.value()
        self._rebuild_grid()

    def _rebuild_grid(self):
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        self._cells.clear()
        for r in range(self._grid_rows):
            for c in range(self._grid_cols):
                cell = CellSlot(r, c)
                cell.clicked.connect(self._on_cell_clicked)
                self._grid_layout.addWidget(cell, r, c)
                self._cells[(r, c)] = cell

        self._update_preview()

    def _on_cell_clicked(self, row: int, col: int):
        """Open config dialog for the clicked cell."""
        cell = self._cells.get((row, col))
        if cell is None:
            return

        dlg = CellConfigDialog(
            self._analyses, self._datasets,
            current_analysis_id=cell.get_analysis_id(),
            current_ds_ids=cell.get_data_source_ids(),
            parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            cell.set_analysis(
                dlg.get_analysis_id(),
                dlg.get_analysis_display_name(),
                dlg.get_selected_ds_ids()
            )
            self._update_preview()

    def _clear_all(self):
        for cell in self._cells.values():
            cell.clear()
        self._update_preview()

    def _update_preview(self):
        self._figure.clear()
        count = sum(1 for c in self._cells.values() if c.get_analysis_id())
        if count == 0:
            ax = self._figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Grid: {self._grid_rows}×{self._grid_cols}\nClick cells to configure',
                    transform=ax.transAxes, ha='center', va='center', fontsize=10)
            ax.axis('off')
        else:
            gs = self._figure.add_gridspec(self._grid_rows, self._grid_cols, hspace=0.5, wspace=0.3)
            for (r, c), cell in self._cells.items():
                ax = self._figure.add_subplot(gs[r, c])
                label = cell._label or 'Empty'
                n_ds = len(cell.get_data_source_ids())
                ds_text = f'\n{n_ds} file(s)' if n_ds else '\nall files'
                ax.text(0.5, 0.5, label + ds_text, transform=ax.transAxes,
                        ha='center', va='center', fontsize=7)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title(f'[{r+1},{c+1}]', fontsize=7, pad=2)
        self._preview_canvas.draw()

    def _save_preset(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Preset', str(Path.home() / '.labanalyzer'), 'JSON (*.json *.labpreset)'
        )
        if path:
            data = {
                'rows': self._grid_rows,
                'cols': self._grid_cols,
                'cells': [
                    {
                        'row': r, 'col': c,
                        'analysis_id': cell.get_analysis_id(),
                        'label': cell._label,
                        'data_source_ids': cell.get_data_source_ids(),
                    }
                    for (r, c), cell in self._cells.items()
                    if cell.get_analysis_id()
                ]
            }
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

    def _load_preset(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Preset', str(Path.home() / '.labanalyzer'), 'JSON (*.json *.labpreset)'
        )
        if path:
            try:
                with open(path) as f:
                    data = json.load(f)
                self._rows_spin.setValue(data.get('rows', 2))
                self._cols_spin.setValue(data.get('cols', 2))
                self._rebuild_grid()
                for cell_data in data.get('cells', []):
                    r, c = cell_data['row'], cell_data['col']
                    cell = self._cells.get((r, c))
                    if cell:
                        cell.set_analysis(
                            cell_data.get('analysis_id', ''),
                            cell_data.get('label', ''),
                            cell_data.get('data_source_ids', []),
                        )
                self._update_preview()
            except Exception as e:
                QMessageBox.warning(self, 'Load Error', str(e))

    def _apply(self):
        cells = []
        for (r, c), cell in self._cells.items():
            if cell.get_analysis_id():
                cells.append(CellConfig(
                    row=r, col=c,
                    analysis_id=cell.get_analysis_id(),
                    data_source_ids=cell.get_data_source_ids(),
                ))
        if not cells:
            QMessageBox.information(self, 'Empty Layout',
                                    'Please configure at least one cell before applying.')
            return
        self.accept()

    def get_layout_config(self) -> CustomLayoutConfig:
        cells = []
        for (r, c), cell in self._cells.items():
            if cell.get_analysis_id():
                cells.append(CellConfig(
                    row=r, col=c,
                    analysis_id=cell.get_analysis_id(),
                    data_source_ids=cell.get_data_source_ids(),
                ))
        return CustomLayoutConfig(rows=self._grid_rows, cols=self._grid_cols, cells=cells)
