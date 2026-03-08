from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class PowerDensityAnalysis(BaseAnalysis):
    analysis_id = 'power_density'
    display_name = 'Power Density'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)
        has_data = False
        cfg = config if isinstance(config, dict) else {}

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            x_col = _find_col(df, ['current density', 'current_density', 'j ('])
            y_col = _find_col(df, ['power density', 'power_density', 'p (', 'power'])
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
            ax.plot(x[:n], y[:n], 's-', color=ds.color or None, label=ds.display_name, markersize=4)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Current Density (mA/cm²)')
        ax.set_ylabel('Power Density (mW/cm²)')
        ax.set_title('Power Density Curve')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
