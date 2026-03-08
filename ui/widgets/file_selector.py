from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QCheckBox, QComboBox,
    QFileDialog, QMenu, QAbstractItemView, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction
from pathlib import Path
from labanalyzer.utils.file_utils import scan_folder, format_file_size


class FileSelectorWidget(QWidget):
    """File/folder picker widget with two panels."""
    files_changed = pyqtSignal(list)  # list of Path objects

    def __init__(self, extensions: list = None, parent=None):
        super().__init__(parent)
        self._extensions = extensions or ['.csv', '.xlsx', '.txt']
        self._files: list[Path] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Left panel: controls
        left = QWidget()
        left.setFixedWidth(200)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        add_files_btn = QPushButton('Add Files...')
        add_files_btn.clicked.connect(self._add_files)
        left_layout.addWidget(add_files_btn)

        add_folder_btn = QPushButton('Add Folder...')
        add_folder_btn.clicked.connect(self._add_folder)
        left_layout.addWidget(add_folder_btn)

        clear_btn = QPushButton('Clear All')
        clear_btn.setObjectName('danger')
        clear_btn.clicked.connect(self._clear)
        left_layout.addWidget(clear_btn)

        self._recursive_check = QCheckBox('Recursive')
        left_layout.addWidget(self._recursive_check)

        # Extension filter
        ext_label = QLabel('Extensions:')
        left_layout.addWidget(ext_label)
        self._ext_combo = QComboBox()
        self._ext_combo.setEditable(True)
        self._ext_combo.addItems(self._extensions)
        left_layout.addWidget(self._ext_combo)

        # File count badge
        self._count_label = QLabel('0 files')
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self._count_label)

        left_layout.addStretch()
        layout.addWidget(left)

        # Right panel: tree view
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(['Name', 'Size'])
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._context_menu)
        self._tree.header().setStretchLastSection(True)
        right_layout.addWidget(self._tree)

        layout.addWidget(right, 1)

    def set_extensions(self, extensions: list):
        self._extensions = extensions
        self._ext_combo.clear()
        self._ext_combo.addItems(extensions)

    def _add_files(self):
        ext_filter = ';;'.join(
            [f'*{e}' for e in self._extensions]
        )
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            'Select Files',
            '',
            f'Data Files ({" ".join(f"*{e}" for e in self._extensions)});;All Files (*)',
        )
        for p in paths:
            path = Path(p)
            if path not in self._files:
                self._files.append(path)
        self._refresh_tree()
        self.files_changed.emit(self._files)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder', '')
        if folder:
            recursive = self._recursive_check.isChecked()
            new_files = scan_folder(folder, self._extensions, recursive)
            for f in new_files:
                if f not in self._files:
                    self._files.append(f)
            self._refresh_tree()
            self.files_changed.emit(self._files)

    def _clear(self):
        self._files.clear()
        self._tree.clear()
        self._count_label.setText('0 files')
        self.files_changed.emit([])

    def _refresh_tree(self):
        self._tree.clear()
        # Group by folder
        groups: dict[str, list[Path]] = {}
        for f in self._files:
            folder = str(f.parent)
            groups.setdefault(folder, []).append(f)

        for folder, files in groups.items():
            folder_item = QTreeWidgetItem([Path(folder).name, ''])
            folder_item.setData(0, Qt.ItemDataRole.UserRole, folder)
            self._tree.addTopLevelItem(folder_item)
            for f in files:
                try:
                    size = format_file_size(f.stat().st_size)
                except OSError:
                    size = '?'
                file_item = QTreeWidgetItem([f.name, size])
                file_item.setData(0, Qt.ItemDataRole.UserRole, str(f))
                folder_item.addChild(file_item)
            folder_item.setExpanded(True)

        self._count_label.setText(f'{len(self._files)} files')

    def _context_menu(self, pos):
        menu = QMenu(self)
        remove_action = QAction('Remove Selected', self)
        remove_action.triggered.connect(self._remove_selected)
        menu.addAction(remove_action)
        menu.exec(self._tree.mapToGlobal(pos))

    def _remove_selected(self):
        selected = self._tree.selectedItems()
        paths_to_remove = set()
        for item in selected:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                paths_to_remove.add(data)
        self._files = [f for f in self._files if str(f) not in paths_to_remove]
        self._refresh_tree()
        self.files_changed.emit(self._files)

    def get_files(self) -> list:
        return list(self._files)

    def set_files(self, files: list):
        self._files = [Path(f) for f in files]
        self._refresh_tree()
