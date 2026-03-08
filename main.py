"""LabAnalyzer - Application entry point."""
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Register all measurements before importing UI
import labanalyzer.measurements  # noqa: F401 - triggers registration

from labanalyzer.app import create_app
from labanalyzer.ui.main_window import MainWindow


def main():
    app, config = create_app()

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
