from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QCheckBox, QLineEdit, QFrame, QColorDialog,
    QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont


class ColorSquare(QFrame):
    """A small clickable colored square."""
    clicked = pyqtSignal(str)  # hex color

    def __init__(self, color: str = '#2E75B6', parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self._color = color
        self._update_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _update_style(self):
        self.setStyleSheet(
            f'background-color: {self._color}; border: 1px solid #888; border-radius: 3px;'
        )

    def mousePressEvent(self, event):
        dlg = QColorDialog(QColor(self._color), self)
        if dlg.exec():
            self._color = dlg.selectedColor().name()
            self._update_style()
            self.clicked.emit(self._color)


class FileRowWidget(QWidget):
    """Single file row with checkbox, color, name edit."""
    visibility_changed = pyqtSignal(bool)
    color_changed = pyqtSignal(str)
    name_changed = pyqtSignal(str)

    def __init__(self, display_name: str, color: str, visible: bool = True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        self._check = QCheckBox()
        self._check.setChecked(visible)
        self._check.toggled.connect(self.visibility_changed)
        layout.addWidget(self._check)

        self._color_sq = ColorSquare(color or '#2E75B6')
        self._color_sq.clicked.connect(self.color_changed)
        layout.addWidget(self._color_sq)

        self._name_edit = QLineEdit(display_name)
        self._name_edit.setFixedHeight(24)
        self._name_edit.editingFinished.connect(lambda: self.name_changed.emit(self._name_edit.text()))
        layout.addWidget(self._name_edit, 1)

        self._edit_btn = QPushButton('✏')
        self._edit_btn.setFixedSize(24, 24)
        self._edit_btn.setObjectName('secondary')
        self._edit_btn.clicked.connect(lambda: self._name_edit.setFocus())
        layout.addWidget(self._edit_btn)

    def set_visible(self, visible: bool, block_signals: bool = False):
        if block_signals:
            self._check.blockSignals(True)
        self._check.setChecked(visible)
        if block_signals:
            self._check.blockSignals(False)

    def set_color(self, color: str):
        self._color_sq._color = color
        self._color_sq._update_style()

    def get_name(self) -> str:
        return self._name_edit.text()

    def set_name(self, name: str):
        self._name_edit.setText(name)

    def is_visible(self) -> bool:
        return self._check.isChecked()


class FolderGroupWidget(QWidget):
    """Folder group header with collapsible file rows."""
    folder_toggled = pyqtSignal(str, bool)  # group_name, checked

    def __init__(self, group_name: str, parent=None):
        super().__init__(parent)
        self.group_name = group_name
        self._rows: list[FileRowWidget] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(1)

        # Header bar
        header = QFrame()
        header.setStyleSheet('QFrame { background: #EEF2F7; border-radius: 3px; }')
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(6, 3, 6, 3)

        self._folder_check = QCheckBox(group_name or 'Ungrouped')
        self._folder_check.setChecked(True)
        font = self._folder_check.font()
        font.setBold(True)
        self._folder_check.setFont(font)
        self._folder_check.toggled.connect(self._on_folder_toggled)
        h_layout.addWidget(self._folder_check)
        h_layout.addStretch()

        self._collapse_btn = QPushButton('▼')
        self._collapse_btn.setFixedSize(20, 20)
        self._collapse_btn.setObjectName('secondary')
        self._collapse_btn.clicked.connect(self._toggle_collapse)
        h_layout.addWidget(self._collapse_btn)
        layout.addWidget(header)

        # Files container (indented)
        self._files_widget = QWidget()
        self._files_layout = QVBoxLayout(self._files_widget)
        self._files_layout.setContentsMargins(16, 0, 0, 0)
        self._files_layout.setSpacing(2)
        layout.addWidget(self._files_widget)

    def add_row(self, row: FileRowWidget):
        self._files_layout.addWidget(row)
        self._rows.append(row)

    @property
    def rows(self) -> list[FileRowWidget]:
        return self._rows

    def _on_folder_toggled(self, checked: bool):
        for row in self._rows:
            row.set_visible(checked, block_signals=True)
        self.folder_toggled.emit(self.group_name, checked)

    def _toggle_collapse(self):
        visible = not self._files_widget.isVisible()
        self._files_widget.setVisible(visible)
        self._collapse_btn.setText('▼' if visible else '▶')

    def update_folder_check(self):
        """Sync folder checkbox to reflect children state."""
        if not self._rows:
            return
        all_checked = all(r.is_visible() for r in self._rows)
        none_checked = not any(r.is_visible() for r in self._rows)
        self._folder_check.blockSignals(True)
        self._folder_check.setChecked(all_checked or (not none_checked))
        self._folder_check.blockSignals(False)


class FileListPanel(QWidget):
    """Right pane: file list with folder hierarchy, visibility checkboxes, color pickers, rename."""
    dataset_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._datasets = []
        self._rows: list[FileRowWidget] = []
        self._groups: dict[str, FolderGroupWidget] = {}
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)

        header = QLabel('Files')
        header.setObjectName('subheading')
        outer.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(4)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content)
        outer.addWidget(self._scroll)

        btn_row = QHBoxLayout()
        all_btn = QPushButton('All')
        all_btn.setObjectName('secondary')
        all_btn.setFixedHeight(24)
        all_btn.clicked.connect(self._select_all)
        btn_row.addWidget(all_btn)

        none_btn = QPushButton('None')
        none_btn.setObjectName('secondary')
        none_btn.setFixedHeight(24)
        none_btn.clicked.connect(self._select_none)
        btn_row.addWidget(none_btn)
        outer.addLayout(btn_row)

    def set_datasets(self, datasets: list):
        """Populate the list, grouping by group_name when multiple groups exist."""
        self._datasets = datasets
        self._rows.clear()
        self._groups.clear()

        # Clear layout (keep trailing stretch)
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Collect unique group names in order
        seen: list[str] = []
        groups: dict[str, list[tuple[int, object]]] = {}
        for i, ds in enumerate(datasets):
            g = ds.group_name or ''
            if g not in groups:
                groups[g] = []
                seen.append(g)
            groups[g].append((i, ds))

        use_groups = len(seen) > 1 or (len(seen) == 1 and seen[0])

        for gname in seen:
            group_widget: FolderGroupWidget | None = None
            if use_groups:
                group_widget = FolderGroupWidget(gname or 'Ungrouped')
                group_widget.folder_toggled.connect(self._on_folder_toggled)
                self._groups[gname] = group_widget

            for ds_idx, ds in groups[gname]:
                row = FileRowWidget(ds.display_name, ds.color, ds.visible)
                row.visibility_changed.connect(
                    lambda checked, i=ds_idx, g=gname: self._on_visibility(i, checked, g)
                )
                row.color_changed.connect(lambda color, i=ds_idx: self._on_color(i, color))
                row.name_changed.connect(lambda name, i=ds_idx: self._on_name(i, name))

                if group_widget is not None:
                    group_widget.add_row(row)
                else:
                    self._content_layout.insertWidget(self._content_layout.count() - 1, row)
                self._rows.append(row)

            if group_widget is not None:
                self._content_layout.insertWidget(self._content_layout.count() - 1, group_widget)

    def _on_folder_toggled(self, group_name: str, checked: bool):
        """Update all datasets in the folder group and re-render."""
        for ds in self._datasets:
            if (ds.group_name or '') == group_name:
                ds.visible = checked
        self.dataset_changed.emit()

    def _on_visibility(self, idx: int, checked: bool, group_name: str = ''):
        if idx < len(self._datasets):
            self._datasets[idx].visible = checked
            if group_name in self._groups:
                self._groups[group_name].update_folder_check()
            self.dataset_changed.emit()

    def _on_color(self, idx: int, color: str):
        if idx < len(self._datasets):
            self._datasets[idx].color = color
            self.dataset_changed.emit()

    def _on_name(self, idx: int, name: str):
        if idx < len(self._datasets):
            self._datasets[idx].display_name = name
            self.dataset_changed.emit()

    def _select_all(self):
        for row in self._rows:
            row.set_visible(True, block_signals=True)
        for ds in self._datasets:
            ds.visible = True
        for gw in self._groups.values():
            gw._folder_check.blockSignals(True)
            gw._folder_check.setChecked(True)
            gw._folder_check.blockSignals(False)
        self.dataset_changed.emit()

    def _select_none(self):
        for row in self._rows:
            row.set_visible(False, block_signals=True)
        for ds in self._datasets:
            ds.visible = False
        for gw in self._groups.values():
            gw._folder_check.blockSignals(True)
            gw._folder_check.setChecked(False)
            gw._folder_check.blockSignals(False)
        self.dataset_changed.emit()
