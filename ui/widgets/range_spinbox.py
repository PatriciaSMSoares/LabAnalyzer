from PyQt6.QtWidgets import QWidget, QHBoxLayout, QDoubleSpinBox, QLabel
from PyQt6.QtCore import pyqtSignal


class RangeSpinBox(QWidget):
    """Dual spinbox for min/max range selection."""
    range_changed = pyqtSignal(object, object)  # min, max (or None)

    def __init__(self, label: str = '', parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label:
            layout.addWidget(QLabel(label))

        self._min_spin = QDoubleSpinBox()
        self._min_spin.setRange(-1e12, 1e12)
        self._min_spin.setDecimals(4)
        self._min_spin.setValue(0.0)
        self._min_spin.setSpecialValueText('Auto')
        self._min_spin.setMinimum(-1e12)

        self._max_spin = QDoubleSpinBox()
        self._max_spin.setRange(-1e12, 1e12)
        self._max_spin.setDecimals(4)
        self._max_spin.setValue(1.0)
        self._max_spin.setSpecialValueText('Auto')

        layout.addWidget(self._min_spin)
        layout.addWidget(QLabel('—'))
        layout.addWidget(self._max_spin)

        self._min_spin.valueChanged.connect(self._on_changed)
        self._max_spin.valueChanged.connect(self._on_changed)

        self._auto_min = True
        self._auto_max = True

    def _on_changed(self):
        self.range_changed.emit(self.get_min(), self.get_max())

    def get_min(self):
        return None if self._auto_min else self._min_spin.value()

    def get_max(self):
        return None if self._auto_max else self._max_spin.value()

    def set_range(self, min_val, max_val):
        if min_val is None:
            self._auto_min = True
        else:
            self._auto_min = False
            self._min_spin.setValue(min_val)

        if max_val is None:
            self._auto_max = True
        else:
            self._auto_max = False
            self._max_spin.setValue(max_val)

    @property
    def min_spinbox(self):
        return self._min_spin

    @property
    def max_spinbox(self):
        return self._max_spin
