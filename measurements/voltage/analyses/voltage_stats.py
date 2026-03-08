from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class VoltageStatsAnalysis(BaseAnalysis):
    analysis_id = 'voltage_stats'
    display_name = 'Voltage Statistics'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)

        has_data = False
        cfg = config if isinstance(config, dict) else {}
        data_arrays = []
        labels = []

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data

            y_col = _find_col(df, ['voltage', 'volt', 'v (', 'potential'])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if y_col is None and len(num_cols) >= 1:
                y_col = num_cols[0]

            if y_col is None:
                continue

            y = df[y_col].dropna().values.astype(float)
            if len(y) == 0:
                continue

            data_arrays.append(y)
            labels.append(ds.display_name[:20])
            has_data = True

        if has_data:
            bp = ax.boxplot(data_arrays, labels=labels, patch_artist=True)
            colors = [ds.color for ds in datasets if ds.visible and ds.color]
            for i, patch in enumerate(bp['boxes']):
                if i < len(colors) and colors[i]:
                    patch.set_facecolor(colors[i])
                    patch.set_alpha(0.6)
            ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax.set_ylabel('Voltage (V)')
        ax.set_title('Voltage Statistics (Box Plot)')
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3, axis='y')

        figure.tight_layout()
