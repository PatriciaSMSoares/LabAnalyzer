from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFormLayout, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QLabel, QGroupBox,
    QPushButton, QHBoxLayout, QFrame, QLineEdit
)
from PyQt6.QtCore import pyqtSignal, Qt
from labanalyzer.core.data_models import PlotConfig, SmoothingConfig
from labanalyzer.core.base_analysis import OptionSpec


class OptionsPanel(QWidget):
    """Left pane options panel."""
    config_changed = pyqtSignal(object)  # PlotConfig
    refresh_requested = pyqtSignal()
    export_plot_requested = pyqtSignal()
    export_data_requested = pyqtSignal()
    custom_plot_requested = pyqtSignal()
    close_tab_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = PlotConfig()
        self._analyses = []
        self._extra_options: list[OptionSpec] = []
        self._extra_widgets: dict[str, QWidget] = {}
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)

        # Section 1: Display Options
        self._display_group = self._make_group('Display Options')
        dform = QFormLayout()
        dform.setSpacing(4)

        self._layout_combo = QComboBox()
        self._layout_combo.addItems(['All in One', 'Grid by Folder', 'Grid by File', 'Side by Side', '2×2 Grid'])
        self._layout_combo.currentTextChanged.connect(self._on_layout_changed)
        dform.addRow('Layout:', self._layout_combo)

        self._analysis_combo = QComboBox()
        self._analysis_combo.currentIndexChanged.connect(self._on_analysis_changed)
        dform.addRow('Analysis:', self._analysis_combo)

        self._colorscheme_combo = QComboBox()
        self._colorscheme_combo.addItems(['Tab10', 'Set2', 'Pastel', 'Dark2'])
        self._colorscheme_combo.currentTextChanged.connect(self._emit_config)
        dform.addRow('Colors:', self._colorscheme_combo)

        self._legend_check = QCheckBox('Show Legend')
        self._legend_check.setChecked(True)
        self._legend_check.toggled.connect(self._emit_config)
        dform.addRow(self._legend_check)

        self._grid_check = QCheckBox('Show Grid')
        self._grid_check.setChecked(True)
        self._grid_check.toggled.connect(self._emit_config)
        dform.addRow(self._grid_check)

        self._display_group.setLayout(dform)
        self._layout.addWidget(self._display_group)

        # Section 2: Axis Range
        self._axis_group = self._make_group('Axis Range')
        aform = QFormLayout()
        aform.setSpacing(4)

        self._xmin = QDoubleSpinBox()
        self._xmin.setRange(-1e9, 1e9)
        self._xmin.setSpecialValueText('Auto')
        self._xmin.setValue(-1e9)
        self._xmax = QDoubleSpinBox()
        self._xmax.setRange(-1e9, 1e9)
        self._xmax.setSpecialValueText('Auto')
        self._xmax.setValue(1e9)

        self._ymin = QDoubleSpinBox()
        self._ymin.setRange(-1e9, 1e9)
        self._ymin.setSpecialValueText('Auto')
        self._ymin.setValue(-1e9)
        self._ymax = QDoubleSpinBox()
        self._ymax.setRange(-1e9, 1e9)
        self._ymax.setSpecialValueText('Auto')
        self._ymax.setValue(1e9)

        xrow = QWidget()
        xl = QHBoxLayout(xrow)
        xl.setContentsMargins(0,0,0,0)
        xl.addWidget(self._xmin)
        xl.addWidget(QLabel('—'))
        xl.addWidget(self._xmax)
        aform.addRow('X Range:', xrow)

        yrow = QWidget()
        yl = QHBoxLayout(yrow)
        yl.setContentsMargins(0,0,0,0)
        yl.addWidget(self._ymin)
        yl.addWidget(QLabel('—'))
        yl.addWidget(self._ymax)
        aform.addRow('Y Range:', yrow)

        self._xlog_check = QCheckBox('X Log Scale')
        self._xlog_check.toggled.connect(self._emit_config)
        aform.addRow(self._xlog_check)

        self._ylog_check = QCheckBox('Y Log Scale')
        self._ylog_check.toggled.connect(self._emit_config)
        aform.addRow(self._ylog_check)

        reset_btn = QPushButton('Reset Ranges')
        reset_btn.setObjectName('secondary')
        reset_btn.clicked.connect(self._reset_ranges)
        aform.addRow(reset_btn)

        self._xmin.valueChanged.connect(self._emit_config)
        self._xmax.valueChanged.connect(self._emit_config)
        self._ymin.valueChanged.connect(self._emit_config)
        self._ymax.valueChanged.connect(self._emit_config)

        self._axis_group.setLayout(aform)
        self._layout.addWidget(self._axis_group)

        # Section 3: Smoothing
        self._smooth_group = self._make_group('Smoothing')
        sform = QFormLayout()
        sform.setSpacing(4)

        self._smooth_method = QComboBox()
        self._smooth_method.addItems(['None', 'Moving Average', 'EMA', 'Gaussian', 'Savitzky-Golay'])
        self._smooth_method.currentTextChanged.connect(self._on_smooth_changed)
        sform.addRow('Method:', self._smooth_method)

        self._smooth_window = QSpinBox()
        self._smooth_window.setRange(3, 1001)
        self._smooth_window.setValue(5)
        self._smooth_window.setSingleStep(2)
        self._smooth_window.valueChanged.connect(self._emit_config)
        sform.addRow('Window:', self._smooth_window)

        self._smooth_sigma = QDoubleSpinBox()
        self._smooth_sigma.setRange(0.1, 100.0)
        self._smooth_sigma.setValue(1.0)
        self._smooth_sigma.valueChanged.connect(self._emit_config)
        sform.addRow('Sigma:', self._smooth_sigma)

        self._smooth_poly = QSpinBox()
        self._smooth_poly.setRange(1, 10)
        self._smooth_poly.setValue(2)
        self._smooth_poly.valueChanged.connect(self._emit_config)
        sform.addRow('Poly Order:', self._smooth_poly)

        self._smooth_group.setLayout(sform)
        self._layout.addWidget(self._smooth_group)

        # Section 4: Analysis-Specific Options
        self._extra_group = self._make_group('Analysis Options')
        self._extra_form = QFormLayout()
        self._extra_form.setSpacing(4)
        self._extra_group.setLayout(self._extra_form)
        self._layout.addWidget(self._extra_group)

        # Section 5: Action Buttons
        self._action_group = self._make_group('Actions')
        action_layout = QVBoxLayout()
        action_layout.setSpacing(4)

        custom_btn = QPushButton('Custom Plot...')
        custom_btn.clicked.connect(self.custom_plot_requested)
        action_layout.addWidget(custom_btn)

        refresh_btn = QPushButton('Refresh Plot')
        refresh_btn.clicked.connect(self.refresh_requested)
        action_layout.addWidget(refresh_btn)

        export_plot_btn = QPushButton('Export Plot...')
        export_plot_btn.setObjectName('secondary')
        export_plot_btn.clicked.connect(self.export_plot_requested)
        action_layout.addWidget(export_plot_btn)

        export_data_btn = QPushButton('Export Data...')
        export_data_btn.setObjectName('secondary')
        export_data_btn.clicked.connect(self.export_data_requested)
        action_layout.addWidget(export_data_btn)

        close_btn = QPushButton('Close Tab')
        close_btn.setObjectName('danger')
        close_btn.clicked.connect(self.close_tab_requested)
        action_layout.addWidget(close_btn)

        self._action_group.setLayout(action_layout)
        self._layout.addWidget(self._action_group)

        self._layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _make_group(self, title: str) -> QGroupBox:
        g = QGroupBox(title)
        return g

    def set_analyses(self, analyses: list):
        """Populate analysis combo from list of analysis classes."""
        self._analyses = analyses
        self._analysis_combo.blockSignals(True)
        self._analysis_combo.clear()
        for a in analyses:
            self._analysis_combo.addItem(a.display_name, a.analysis_id)
        self._analysis_combo.blockSignals(False)
        if analyses:
            self._update_extra_options(analyses[0])
            self._config.analysis_id = analyses[0].analysis_id

    def _on_analysis_changed(self, idx: int):
        if 0 <= idx < len(self._analyses):
            analysis = self._analyses[idx]
            self._config.analysis_id = analysis.analysis_id
            self._update_extra_options(analysis)
            self._emit_config()

    def _update_extra_options(self, analysis_cls):
        # Clear existing extra options
        while self._extra_form.rowCount() > 0:
            self._extra_form.removeRow(0)
        self._extra_widgets.clear()

        options = analysis_cls.get_extra_options()
        self._extra_options = options

        if not options:
            self._extra_group.setVisible(False)
            return

        self._extra_group.setVisible(True)
        for opt in options:
            widget = self._make_option_widget(opt)
            if widget:
                self._extra_form.addRow(opt.label + ':', widget)
                self._extra_widgets[opt.key] = widget

    def _make_option_widget(self, opt: OptionSpec) -> QWidget | None:
        if opt.widget_type == 'combobox':
            w = QComboBox()
            w.addItems([str(o) for o in opt.options])
            if opt.default is not None and str(opt.default) in opt.options:
                w.setCurrentText(str(opt.default))
            w.currentTextChanged.connect(self._emit_config)
            return w
        elif opt.widget_type == 'spinbox':
            w = QDoubleSpinBox()
            w.setRange(opt.min_val, opt.max_val)
            if opt.default is not None:
                w.setValue(float(opt.default))
            w.valueChanged.connect(self._emit_config)
            return w
        elif opt.widget_type == 'checkbox':
            w = QCheckBox()
            if opt.default:
                w.setChecked(bool(opt.default))
            w.toggled.connect(self._emit_config)
            return w
        elif opt.widget_type == 'lineedit':
            w = QLineEdit()
            if opt.default is not None:
                w.setText(str(opt.default))
            w.editingFinished.connect(self._emit_config)
            return w
        return None

    def _on_layout_changed(self, text: str):
        self._config.layout = text
        self._emit_config()

    def _on_smooth_changed(self, method: str):
        visible = method != 'None'
        self._smooth_window.setVisible(visible)
        self._smooth_sigma.setVisible(method in ['Gaussian'])
        self._smooth_poly.setVisible(method in ['Savitzky-Golay'])
        self._emit_config()

    def _reset_ranges(self):
        self._config.x_min = None
        self._config.x_max = None
        self._config.y_min = None
        self._config.y_max = None
        self._emit_config()

    def _emit_config(self, *args):
        cfg = self.get_config()
        self.config_changed.emit(cfg)

    def get_config(self) -> PlotConfig:
        cfg = PlotConfig(
            analysis_id=self._analysis_combo.currentData() or '',
            layout=self._layout_combo.currentText(),
            show_legend=self._legend_check.isChecked(),
            show_grid=self._grid_check.isChecked(),
            x_log=self._xlog_check.isChecked(),
            y_log=self._ylog_check.isChecked(),
            smoothing=SmoothingConfig(
                method=self._smooth_method.currentText(),
                window=self._smooth_window.value(),
                sigma=self._smooth_sigma.value(),
                poly_order=self._smooth_poly.value(),
            ),
            extra=self._get_extra_values(),
        )
        # Ranges
        xmin = self._xmin.value()
        xmax = self._xmax.value()
        ymin = self._ymin.value()
        ymax = self._ymax.value()
        cfg.x_min = None if xmin == -1e9 else xmin
        cfg.x_max = None if xmax == 1e9 else xmax
        cfg.y_min = None if ymin == -1e9 else ymin
        cfg.y_max = None if ymax == 1e9 else ymax
        return cfg

    def _get_extra_values(self) -> dict:
        values = {'color_scheme': self._colorscheme_combo.currentText()}
        for opt in self._extra_options:
            w = self._extra_widgets.get(opt.key)
            if w is None:
                continue
            if isinstance(w, QComboBox):
                values[opt.key] = w.currentText()
            elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                values[opt.key] = w.value()
            elif isinstance(w, QCheckBox):
                values[opt.key] = w.isChecked()
            elif isinstance(w, QLineEdit):
                values[opt.key] = w.text()
        return values

    def get_selected_analysis_id(self) -> str:
        return self._analysis_combo.currentData() or ''

    def get_color_scheme(self) -> str:
        return self._colorscheme_combo.currentText()

    def set_layout(self, layout: str):
        """Set layout combo to a given value (adds it if not present)."""
        idx = self._layout_combo.findText(layout)
        if idx < 0:
            self._layout_combo.addItem(layout)
            idx = self._layout_combo.count() - 1
        self._layout_combo.blockSignals(True)
        self._layout_combo.setCurrentIndex(idx)
        self._layout_combo.blockSignals(False)
