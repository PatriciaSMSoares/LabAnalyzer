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


class TGADSCAnalysis(BaseAnalysis):
    analysis_id = 'tga_dsc'
    display_name = 'TGA + DSC (Dual-Y)'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax1 = figure.add_subplot(111)
        else:
            ax1 = ax
        ax2 = ax1.twinx()
        has_data = False
        cfg = config if isinstance(config, dict) else {}
        smoothing = cfg.get('smoothing', SmoothingConfig())

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            x_col = _find_col(df, ['temperature', 'temp', '°c'])
            mass_col = _find_col(df, ['mass', 'weight', 'mass%'])
            dsc_col = _find_col(df, ['heat flow', 'heat_flow', 'dsc', 'mw'])

            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if mass_col is None and len(num_cols) >= 2:
                mass_col = num_cols[1]
            if dsc_col is None and len(num_cols) >= 3:
                dsc_col = num_cols[2]

            if x_col is None:
                continue
            x = df[x_col].dropna().values.astype(float)
            color = ds.color or None

            if mass_col is not None:
                y1 = df[mass_col].dropna().values.astype(float)
                n = min(len(x), len(y1))
                if smoothing and smoothing.method != 'None':
                    y1 = apply_smoothing(y1, smoothing)
                ax1.plot(x[:n], y1[:n], '-', color=color, label=f'{ds.display_name} (TGA)', linewidth=1.5)

            if dsc_col is not None:
                y2 = df[dsc_col].dropna().values.astype(float)
                n2 = min(len(x), len(y2))
                if smoothing and smoothing.method != 'None':
                    y2 = apply_smoothing(y2, smoothing)
                ax2.plot(x[:n2], y2[:n2], '--', color=color, label=f'{ds.display_name} (DSC)', linewidth=1.5, alpha=0.7)

            has_data = True

        if not has_data:
            ax1.text(0.5, 0.5, 'No data available', transform=ax1.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax1.set_xlabel('Temperature (°C)')
        ax1.set_ylabel('Mass (%)', color='tab:blue')
        ax2.set_ylabel('Heat Flow (mW)', color='tab:orange')
        ax1.set_title('TGA + DSC Combined')

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        if cfg.get('show_legend', True) and has_data:
            ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8)
        if cfg.get('show_grid', True):
            ax1.grid(True, alpha=0.3)
        figure.tight_layout()
