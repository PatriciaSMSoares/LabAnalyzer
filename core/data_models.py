from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd


@dataclass
class DataSet:
    file_path: Path
    display_name: str
    raw_data: pd.DataFrame
    group_name: str = ''
    color: str = ''
    visible: bool = True


@dataclass
class MassEntry:
    sample_id: str
    mass_mg: float


@dataclass
class SmoothingConfig:
    method: str = 'None'
    window: int = 5
    sigma: float = 1.0
    poly_order: int = 2


@dataclass
class PlotConfig:
    analysis_id: str = ''
    layout: str = 'All in One'
    x_min: float | None = None
    x_max: float | None = None
    y_min: float | None = None
    y_max: float | None = None
    x_log: bool = False
    y_log: bool = False
    show_legend: bool = True
    show_grid: bool = True
    smoothing: SmoothingConfig = field(default_factory=SmoothingConfig)
    extra: dict = field(default_factory=dict)


@dataclass
class CellConfig:
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1
    analysis_id: str = ''
    data_source_ids: list = field(default_factory=list)
    plot_config: PlotConfig | None = None
    row_weight: float = 1.0
    col_weight: float = 1.0


@dataclass
class CustomLayoutConfig:
    rows: int = 2
    cols: int = 2
    cells: list = field(default_factory=list)
    preset_name: str = ''

    def to_gridspec_kwargs(self) -> dict:
        height = [1.0] * self.rows
        width = [1.0] * self.cols
        for cell in self.cells:
            height[cell.row] = max(height[cell.row], cell.row_weight)
            width[cell.col] = max(width[cell.col], cell.col_weight)
        return {'height_ratios': height, 'width_ratios': width}
