import time
import traceback
from math import ceil
from pathlib import Path
from matplotlib.figure import Figure as MplFigure

from PyQt6.QtWidgets import (
    QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QFrame, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QRunnable, QThreadPool, QObject, pyqtSignal
from PyQt6.QtGui import QFont

from labanalyzer.core.data_models import PlotConfig, DataSet, SmoothingConfig, CustomLayoutConfig
from labanalyzer.core.smoothing import apply_smoothing
from labanalyzer.utils.color_cycle import ColorCycle
from labanalyzer.ui.widgets.options_panel import OptionsPanel
from labanalyzer.ui.widgets.plot_canvas import PlotCanvas
from labanalyzer.ui.widgets.file_list_panel import FileListPanel


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(float)  # elapsed time


class RenderWorker(QRunnable):
    def __init__(self, fn, *args):
        super().__init__()
        self.fn = fn
        self.args = args
        self.signals = WorkerSignals()

    def run(self):
        try:
            start = time.perf_counter()
            self.fn(*self.args)
            elapsed = time.perf_counter() - start
            self.signals.result.emit(elapsed)
        except Exception as e:
            self.signals.error.emit(traceback.format_exc())
        finally:
            self.signals.finished.emit()


def _build_subplot_grid(figure, layout: str, datasets: list) -> list:
    """
    Clear figure and return list of (ax, dataset_subset) pairs based on layout mode.
    Does NOT call figure.clear() when layout is 'All in One' so the analysis can
    manage clearing itself for the single-ax case.
    """
    n = len(datasets)
    if n == 0:
        return []

    match layout:
        case 'Grid by Folder':
            groups: dict[str, list] = {}
            for ds in datasets:
                groups.setdefault(ds.group_name or 'Default', []).append(ds)
            n_groups = len(groups)
            cols = min(2, n_groups)
            rows = ceil(n_groups / cols)
            figure.clear()
            result = []
            for i, (gname, gds) in enumerate(groups.items()):
                ax = figure.add_subplot(rows, cols, i + 1)
                ax.set_title(gname, fontsize=9)
                result.append((ax, gds))
            return result

        case 'Grid by File':
            cols = min(3, n)
            rows = ceil(n / cols)
            figure.clear()
            result = []
            for i, ds in enumerate(datasets):
                ax = figure.add_subplot(rows, cols, i + 1)
                result.append((ax, [ds]))
            return result

        case 'Side by Side':
            figure.clear()
            result = []
            for i, ds in enumerate(datasets):
                ax = figure.add_subplot(1, n, i + 1)
                result.append((ax, [ds]))
            return result

        case '2×2 Grid':
            figure.clear()
            result = []
            for i, ds in enumerate(datasets[:4]):
                ax = figure.add_subplot(2, 2, i + 1)
                result.append((ax, [ds]))
            return result

        case _:  # 'All in One' — let analysis manage its own figure.clear()
            return [(None, datasets)]


def _render_custom_layout(figure, custom_config: CustomLayoutConfig,
                          datasets: list, analyses: list, config_dict: dict):
    """Render a CustomLayoutConfig into the figure using GridSpec."""
    from matplotlib.gridspec import GridSpec

    figure.clear()
    gs = GridSpec(custom_config.rows, custom_config.cols,
                  figure=figure, **custom_config.to_gridspec_kwargs())

    analysis_map = {a.analysis_id: a for a in analyses}

    for cell in custom_config.cells:
        if not cell.analysis_id:
            continue
        analysis_cls = analysis_map.get(cell.analysis_id)
        if analysis_cls is None:
            continue

        ax = figure.add_subplot(
            gs[cell.row: cell.row + cell.row_span,
               cell.col: cell.col + cell.col_span]
        )

        if cell.data_source_ids:
            # Use specific files selected for this cell (regardless of visibility toggle)
            id_set = set(cell.data_source_ids)
            cell_ds = [ds for ds in datasets if str(ds.file_path) in id_set]
        else:
            # No specific selection → show all currently visible datasets
            cell_ds = [ds for ds in datasets if ds.visible]

        effective_cfg = config_dict
        if cell.plot_config is not None:
            effective_cfg = {
                'analysis_id': cell.plot_config.analysis_id,
                'layout': cell.plot_config.layout,
                'x_min': cell.plot_config.x_min,
                'x_max': cell.plot_config.x_max,
                'y_min': cell.plot_config.y_min,
                'y_max': cell.plot_config.y_max,
                'x_log': cell.plot_config.x_log,
                'y_log': cell.plot_config.y_log,
                'show_legend': cell.plot_config.show_legend,
                'show_grid': cell.plot_config.show_grid,
                'smoothing': cell.plot_config.smoothing,
                'extra': cell.plot_config.extra,
            }

        try:
            analysis_cls().render(cell_ds, effective_cfg, figure, ax=ax)
        except Exception:
            ax.text(0.5, 0.5, f'{analysis_cls.display_name}\n(render error)',
                    transform=ax.transAxes, ha='center', va='center',
                    fontsize=9, color='red')


class AnalysisTab(QWidget):
    """Analysis tab with three-pane splitter layout."""
    render_complete = pyqtSignal(float)
    status_message = pyqtSignal(str)
    close_requested = pyqtSignal()

    def __init__(self, datasets: list, measurement_cls, parent=None):
        super().__init__(parent)
        self._datasets = datasets
        self._measurement_cls = measurement_cls
        self._analyses = measurement_cls.get_analyses()
        self._color_cycle = ColorCycle()
        self._color_cycle.assign_colors(datasets)
        self._render_timer = QTimer()
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._do_render)
        self._rendering = False
        self._thread_pool = QThreadPool.globalInstance()
        self._current_config = PlotConfig()
        if self._analyses:
            self._current_config.analysis_id = self._analyses[0].analysis_id
        self._custom_layout_config: CustomLayoutConfig | None = None
        self._custom_layout_active: bool = False
        self._last_color_scheme = 'Tab10'
        self._setup_ui()
        QTimer.singleShot(100, self._do_render)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Error banner
        self._error_widget = QFrame()
        self._error_widget.setObjectName('error_banner')
        err_layout = QHBoxLayout(self._error_widget)
        self._error_label = QLabel()
        self._error_label.setWordWrap(True)
        err_layout.addWidget(self._error_label, 1)
        self._error_detail_btn = QPushButton('Details')
        self._error_detail_btn.setObjectName('secondary')
        self._error_detail_btn.setFixedWidth(70)
        self._error_detail_btn.clicked.connect(self._show_error_details)
        err_layout.addWidget(self._error_detail_btn)
        dismiss_btn = QPushButton('✕')
        dismiss_btn.setObjectName('secondary')
        dismiss_btn.setFixedWidth(30)
        dismiss_btn.clicked.connect(lambda: self._error_widget.setVisible(False))
        err_layout.addWidget(dismiss_btn)
        self._error_widget.setVisible(False)
        self._last_error = ''
        layout.addWidget(self._error_widget)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._options_panel = OptionsPanel()
        self._options_panel.setMinimumWidth(240)
        self._options_panel.setMaximumWidth(360)
        self._options_panel.set_analyses(self._analyses)
        self._options_panel.config_changed.connect(self._on_config_changed)
        self._options_panel.refresh_requested.connect(self._do_render)
        self._options_panel.export_plot_requested.connect(self._export_plot)
        self._options_panel.export_data_requested.connect(self._export_data)
        self._options_panel.custom_plot_requested.connect(self._open_custom_layout)
        self._options_panel.close_tab_requested.connect(self.close_requested)
        splitter.addWidget(self._options_panel)

        self._plot_canvas = PlotCanvas()
        splitter.addWidget(self._plot_canvas)

        self._file_list = FileListPanel()
        self._file_list.setMinimumWidth(200)
        self._file_list.setMaximumWidth(320)
        self._file_list.set_datasets(self._datasets)
        self._file_list.dataset_changed.connect(self._on_dataset_changed)
        splitter.addWidget(self._file_list)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([280, 700, 240])
        layout.addWidget(splitter)

    def _on_config_changed(self, config: PlotConfig):
        # Re-assign colors when color scheme changes
        new_scheme = config.extra.get('color_scheme', 'Tab10')
        if new_scheme != self._last_color_scheme:
            self._last_color_scheme = new_scheme
            self._color_cycle.set_palette(new_scheme)
            self._color_cycle.reset()
            for ds in self._datasets:
                ds.color = ''
            self._color_cycle.assign_colors(self._datasets)
            self._file_list.set_datasets(self._datasets)

        # If user explicitly selects a standard (non-custom) layout, deactivate custom layout
        if self._custom_layout_active and not config.layout.startswith('Custom'):
            self._custom_layout_active = False
            self._custom_layout_config = None

        # Normalize layout string — keep 'Custom' marker when custom is active
        if self._custom_layout_active:
            config.layout = 'Custom'

        self._current_config = config
        self._render_timer.start(50)

    def _on_dataset_changed(self):
        self._render_timer.start(150)

    def _do_render(self):
        if self._rendering:
            return
        self._rendering = True

        analysis_id = self._current_config.analysis_id
        analysis_cls = next((a for a in self._analyses if a.analysis_id == analysis_id), None)
        if analysis_cls is None and self._analyses:
            analysis_cls = self._analyses[0]
        if analysis_cls is None:
            self._rendering = False
            return

        visible_datasets = [ds for ds in self._datasets if ds.visible]
        if not visible_datasets:
            # Main-thread safe: directly update the canvas figure
            fig = self._plot_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No files selected for display',
                    transform=ax.transAxes, ha='center', va='center',
                    fontsize=14, color='gray')
            self._plot_canvas.canvas.draw_idle()
            self._rendering = False
            return

        cfg = self._current_config
        config_dict = {
            'analysis_id': cfg.analysis_id,
            'layout': cfg.layout,
            'x_min': cfg.x_min,
            'x_max': cfg.x_max,
            'y_min': cfg.y_min,
            'y_max': cfg.y_max,
            'x_log': cfg.x_log,
            'y_log': cfg.y_log,
            'show_legend': cfg.show_legend,
            'show_grid': cfg.show_grid,
            'smoothing': cfg.smoothing,
            'extra': cfg.extra,
        }

        # Create a detached figure for background-thread rendering.
        # This avoids the matplotlib/Qt thread-safety race condition where
        # Qt's paint event reads the canvas figure while the worker modifies it.
        old_fig = self._plot_canvas.figure
        new_fig = MplFigure(figsize=old_fig.get_size_inches(), dpi=old_fig.dpi)
        new_fig.patch.set_facecolor(old_fig.get_facecolor())

        layout_mode = cfg.layout
        custom_config = self._custom_layout_config
        custom_active = self._custom_layout_active
        all_datasets = self._datasets
        analyses = self._analyses
        analysis_instance = analysis_cls()

        def render_fn():
            # All matplotlib operations run on new_fig (not attached to any Qt widget)
            if custom_active and custom_config is not None:
                _render_custom_layout(new_fig, custom_config, all_datasets,
                                      analyses, config_dict)
            else:
                subplot_data = _build_subplot_grid(new_fig, layout_mode, visible_datasets)
                for ax, ds_subset in subplot_data:
                    if ds_subset:
                        analysis_instance.render(ds_subset, config_dict, new_fig, ax=ax)

            # Apply axis ranges to every axes in the new figure
            for ax in new_fig.get_axes():
                if cfg.x_min is not None or cfg.x_max is not None:
                    current = ax.get_xlim()
                    xmin = cfg.x_min if cfg.x_min is not None else current[0]
                    xmax = cfg.x_max if cfg.x_max is not None else current[1]
                    ax.set_xlim(xmin, xmax)
                if cfg.y_min is not None or cfg.y_max is not None:
                    current = ax.get_ylim()
                    ymin = cfg.y_min if cfg.y_min is not None else current[0]
                    ymax = cfg.y_max if cfg.y_max is not None else current[1]
                    ax.set_ylim(ymin, ymax)
                if cfg.x_log:
                    try:
                        ax.set_xscale('log')
                    except Exception:
                        pass
                if cfg.y_log:
                    try:
                        ax.set_yscale('log')
                    except Exception:
                        pass

        worker = RenderWorker(render_fn)
        worker.signals.result.connect(lambda elapsed: self._on_render_complete(elapsed, new_fig))
        worker.signals.error.connect(self._on_render_error)
        worker.signals.finished.connect(lambda: setattr(self, '_rendering', False))
        self._thread_pool.start(worker)

    def _on_render_complete(self, elapsed: float, new_fig: MplFigure | None = None):
        # Swap the rendered figure into the canvas (main thread — Qt-safe)
        if new_fig is not None:
            old_fig = self._plot_canvas.figure
            self._plot_canvas.figure = new_fig
            self._plot_canvas.canvas.figure = new_fig
            new_fig.set_canvas(self._plot_canvas.canvas)
            old_fig.set_canvas(None)
        self._plot_canvas.canvas.draw_idle()
        self._error_widget.setVisible(False)
        self.render_complete.emit(elapsed)
        self.status_message.emit(f'Rendered in {elapsed*1000:.0f}ms')

    def _on_render_error(self, error: str):
        self._last_error = error
        short = error.split('\n')[-2] if '\n' in error else error[:80]
        self._error_label.setText(f'Render error: {short}')
        self._error_widget.setVisible(True)
        self._plot_canvas.canvas.draw_idle()

    def _show_error_details(self):
        QMessageBox.critical(self, 'Render Error', self._last_error)

    def _export_plot(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Export Plot', '', 'PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;All Files (*)'
        )
        if path:
            try:
                self._plot_canvas.figure.savefig(path, dpi=150, bbox_inches='tight')
                self.status_message.emit(f'Plot saved to {Path(path).name}')
            except Exception as e:
                QMessageBox.warning(self, 'Export Error', str(e))

    def _export_data(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Export Data', '', 'CSV (*.csv);;Excel (*.xlsx);;All Files (*)'
        )
        if not path:
            return
        try:
            import pandas as pd
            dfs = [ds.raw_data.copy().assign(_source=ds.display_name)
                   for ds in self._datasets if ds.visible]
            if dfs:
                combined = pd.concat(dfs, ignore_index=True)
                if path.endswith('.xlsx'):
                    combined.to_excel(path, index=False)
                else:
                    combined.to_csv(path, index=False)
                self.status_message.emit(f'Data saved to {Path(path).name}')
        except Exception as e:
            QMessageBox.warning(self, 'Export Error', str(e))

    def _open_custom_layout(self):
        from labanalyzer.ui.custom_layout_builder import CustomLayoutBuilder
        dlg = CustomLayoutBuilder(self._datasets, self._analyses, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._custom_layout_config = dlg.get_layout_config()
            self._custom_layout_active = True
            label = f'Custom ({self._custom_layout_config.rows}×{self._custom_layout_config.cols})'
            self._options_panel.set_layout(label)
            self._current_config.layout = 'Custom'
            # Use timer so the render fires even if a previous render is in progress
            self._render_timer.start(50)

    def get_visible_count(self) -> int:
        return sum(1 for ds in self._datasets if ds.visible)
