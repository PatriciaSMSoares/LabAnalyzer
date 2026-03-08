from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    """App-wide signal bus."""
    measurement_selected = pyqtSignal(str)          # measurement_id
    files_changed = pyqtSignal(list)                # list of file paths
    plot_config_changed = pyqtSignal(object)        # PlotConfig
    render_requested = pyqtSignal()
    render_complete = pyqtSignal(float)             # elapsed seconds
    error_occurred = pyqtSignal(str)               # error message
    status_message = pyqtSignal(str)               # status bar message


# Singleton
_signals: AppSignals | None = None


def get_signals() -> AppSignals:
    global _signals
    if _signals is None:
        _signals = AppSignals()
    return _signals
