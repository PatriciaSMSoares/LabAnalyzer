from labanalyzer.core.base_analysis import BaseAnalysis, OptionSpec
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class PoreSizeDistDifVolAnalysis(BaseAnalysis):
    analysis_id = 'psdDifVol'
    display_name = 'Differential Volume Pore Size Distribution (dV vs Pore Width)'

    @classmethod
    def get_extra_options(cls):
        return [
            OptionSpec(
                key='method',
                label='Method',
                widget_type='combobox',
                options=['BJH', 'DFT'],
                default='BJH',
            )
        ]

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

            x_col = _find_col(df, ['pore width', 'pore diameter', 'pore size', 'diameter', 'width', 'pore'])
            y_col = _find_col(df, ['Dv', 'differential volume'])

            print(f"Dataset: {ds.display_name}, x_col: {x_col}, y_col: {y_col}")

            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if y_col is None and len(num_cols) >= 2:
                y_col = num_cols[1]

            if x_col is None or y_col is None:
                continue

            x = df[x_col].dropna().values.astype(float)
            y = df[y_col].dropna().values.astype(float)
            min_len = min(len(x), len(y))
            x = x[:min_len]
            y = y[:min_len]

            if len(x) == 0:
                continue

            color = ds.color or None
            ax.plot(x, y, '.-', color=color, label=ds.display_name, linewidth=1.5)
            ax.fill_between(x, y, alpha=0.2, color=color)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        method = cfg.get('extra', {}).get('method', 'BJH')
        ax.set_xlabel('Pore Width (nm)')
        ax.set_ylabel('Differential Volume (cm³/µm-g)')
        ax.set_title(f'Differential Volume Pore Size Distribution ({method})')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        if cfg.get('x_log', False):
            ax.set_xscale('log')

        figure.tight_layout()
