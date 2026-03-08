from labanalyzer.core.base_analysis import BaseAnalysis
from labanalyzer.core.smoothing import apply_smoothing
from labanalyzer.core.data_models import SmoothingConfig
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class DSCAnalysis(BaseAnalysis):
    analysis_id = 'dsc'
    display_name = 'DSC (Heat Flow)'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)
        has_data = False
        cfg = config if isinstance(config, dict) else {}
        smoothing = cfg.get('smoothing', SmoothingConfig())

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            x_col = _find_col(df, ['temperature', 'temp', '°c'])
            y_col = _find_col(df, ['heat flow', 'heat_flow', 'dsc', 'heatflow', 'mw'])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if y_col is None and len(num_cols) >= 2:
                y_col = num_cols[1]
            if x_col is None or y_col is None:
                continue
            x = df[x_col].dropna().values.astype(float)
            y = df[y_col].dropna().values.astype(float)
            n = min(len(x), len(y))
            x, y = x[:n], y[:n]
            if smoothing and smoothing.method != 'None':
                y = apply_smoothing(y, smoothing)
            ax.plot(x, y, '-', color=ds.color or None, label=ds.display_name, linewidth=1.5)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No DSC data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Heat Flow (mW)')
        ax.set_title('DSC Curve')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
