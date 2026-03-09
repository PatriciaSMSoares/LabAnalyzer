"""LabAnalyzer - Application entry point."""
import sys
import traceback
import logging
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Register all measurements before importing UI
import labanalyzer.measurements  # noqa: F401 - triggers registration

from labanalyzer.app import create_app
from labanalyzer.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def _install_exception_hooks():
    """Prevent unhandled exceptions from silently terminating the process."""

    def excepthook(exctype, value, tb):
        logger.error("Unhandled exception", exc_info=(exctype, value, tb))
        traceback.print_exception(exctype, value, tb)
        # Show a dialog if a QApplication exists
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app is not None:
                msg = ''.join(traceback.format_exception(exctype, value, tb))
                QMessageBox.critical(
                    None,
                    'Unexpected Error',
                    f'An unexpected error occurred:\n\n{exctype.__name__}: {value}\n\n'
                    f'The application will try to continue.\n\nDetails:\n{msg[-1000:]}',
                )
        except Exception:
            pass  # don't let the error handler itself crash

    sys.excepthook = excepthook


def main():
    _install_exception_hooks()
    app, config = create_app()

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
