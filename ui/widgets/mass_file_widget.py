from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
import pandas as pd


class MassFileWidget(QWidget):
    """Excel mass-file picker and display widget."""
    mass_data_changed = pyqtSignal(list)  # list of MassEntry

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mass_entries = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel('Mass File (Excel/CSV):')
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        self._path_label = QLabel('No file loaded')
        self._path_label.setWordWrap(True)
        btn_layout.addWidget(self._path_label, 1)

        self._browse_btn = QPushButton('Browse...')
        self._browse_btn.setFixedWidth(80)
        self._browse_btn.clicked.connect(self._browse)
        btn_layout.addWidget(self._browse_btn)

        self._clear_btn = QPushButton('Clear')
        self._clear_btn.setObjectName('secondary')
        self._clear_btn.setFixedWidth(60)
        self._clear_btn.clicked.connect(self._clear)
        btn_layout.addWidget(self._clear_btn)
        layout.addLayout(btn_layout)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(['Sample ID', 'Mass (mg)'])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setMaximumHeight(110)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Load Mass File',
            '',
            'Data Files (*.xlsx *.xls *.csv);;All Files (*)',
        )
        if path:
            self._load_file(Path(path))

    def _load_file(self, path: Path):
        try:
            if path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)

            self._mass_entries = []
            self._table.setRowCount(0)

            from labanalyzer.core.data_models import MassEntry
            for _, row in df.iterrows():
                vals = list(row)
                if len(vals) >= 2:
                    try:
                        entry = MassEntry(str(vals[0]), float(vals[1]))
                        self._mass_entries.append(entry)
                        r = self._table.rowCount()
                        self._table.insertRow(r)
                        self._table.setItem(r, 0, QTableWidgetItem(entry.sample_id))
                        self._table.setItem(r, 1, QTableWidgetItem(f'{entry.mass_mg:.4f}'))
                    except (ValueError, TypeError):
                        continue

            self._path_label.setText(path.name)
            self.mass_data_changed.emit(self._mass_entries)

        except Exception as e:
            QMessageBox.warning(self, 'Mass File Error', f'Failed to load mass file:\n{e}')

    def _clear(self):
        self._mass_entries = []
        self._table.setRowCount(0)
        self._path_label.setText('No file loaded')
        self.mass_data_changed.emit([])

    def get_mass_entries(self) -> list:
        return self._mass_entries

    def has_data(self) -> bool:
        return len(self._mass_entries) > 0
