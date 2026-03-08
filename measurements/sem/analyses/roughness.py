from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class RoughnessAnalysis(BaseAnalysis):
    analysis_id = 'roughness'
    display_name = 'Roughness (Ra/Rq)'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)
        has_data = False
        cfg = config if isinstance(config, dict) else {}

        names = []
        ra_vals = []
        rq_vals = []
        colors = []

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            z_col = _find_col(df, ['height', 'z (', 'roughness', 'surface', 'profile'])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if z_col is None and len(num_cols) >= 1:
                z_col = num_cols[0]
            if z_col is None:
                continue
            z = df[z_col].dropna().values.astype(float)
            if len(z) == 0:
                continue
            z_mean = np.mean(z)
            Ra = np.mean(np.abs(z - z_mean))
            Rq = np.sqrt(np.mean((z - z_mean)**2))
            names.append(ds.display_name[:15])
            ra_vals.append(Ra)
            rq_vals.append(Rq)
            colors.append(ds.color or None)
            has_data = True

        if has_data:
            x = np.arange(len(names))
            width = 0.35
            ax.bar(x - width/2, ra_vals, width, label='Ra', alpha=0.7)
            ax.bar(x + width/2, rq_vals, width, label='Rq', alpha=0.7)
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=30, ha='right', fontsize=8)
            ax.legend(fontsize=8)
        else:
            ax.text(0.5, 0.5, 'No roughness data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax.set_ylabel('Roughness (nm)')
        ax.set_title('Surface Roughness Parameters')
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3, axis='y')
        figure.tight_layout()
