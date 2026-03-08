from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure


class PlotCanvas(QWidget):
    """Matplotlib Qt canvas with navigation toolbar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_facecolor('#FFFFFF')

        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def get_figure(self) -> Figure:
        return self.figure

    def refresh(self):
        self.canvas.draw_idle()

    def clear(self):
        self.figure.clear()
        self.canvas.draw_idle()

    def set_background_color(self, color: str):
        self.figure.patch.set_facecolor(color)
        for ax in self.figure.get_axes():
            ax.set_facecolor(color)
        self.canvas.draw_idle()
