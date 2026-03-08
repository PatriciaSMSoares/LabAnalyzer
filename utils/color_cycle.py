import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class ColorCycle:
    """Assigns consistent colors to datasets from matplotlib colormaps."""

    PALETTES = {
        'Tab10': plt.cm.tab10.colors,
        'Set2': plt.cm.Set2.colors,
        'Pastel': plt.cm.Pastel1.colors,
        'Dark2': plt.cm.Dark2.colors,
    }

    def __init__(self, palette: str = 'Tab10'):
        self._palette = palette
        self._colors = list(self.PALETTES.get(palette, self.PALETTES['Tab10']))
        self._assignments: dict[str, str] = {}
        self._index = 0

    def get_color(self, dataset_id: str) -> str:
        """Get consistent hex color for a dataset identifier."""
        if dataset_id not in self._assignments:
            color = self._colors[self._index % len(self._colors)]
            if isinstance(color, tuple):
                color = mcolors.to_hex(color)
            self._assignments[dataset_id] = color
            self._index += 1
        return self._assignments[dataset_id]

    def assign_colors(self, datasets: list) -> None:
        """Assign colors to a list of DataSet objects in-place."""
        for ds in datasets:
            if not ds.color:
                ds.color = self.get_color(str(ds.file_path))

    def reset(self) -> None:
        """Reset all color assignments."""
        self._assignments.clear()
        self._index = 0

    def set_palette(self, palette: str) -> None:
        """Change the active palette."""
        self._palette = palette
        self._colors = list(self.PALETTES.get(palette, self.PALETTES['Tab10']))
