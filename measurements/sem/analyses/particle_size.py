from labanalyzer.core.base_analysis import BaseAnalysis, OptionSpec
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class ParticleSizeAnalysis(BaseAnalysis):
    analysis_id = 'particle_size'
    display_name = 'Particle Size Distribution'

    @classmethod
    def get_extra_options(cls):
        return [
            OptionSpec(key='bins', label='Histogram Bins', widget_type='spinbox',
                       default=20, min_val=5, max_val=200),
        ]

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)
        has_data = False
        cfg = config if isinstance(config, dict) else {}
        bins = int(cfg.get('extra', {}).get('bins', 20))

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            size_col = _find_col(df, ['size', 'diameter', 'particle', 'radius', 'd ('])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if size_col is None and len(num_cols) >= 1:
                size_col = num_cols[0]
            if size_col is None:
                continue
            sizes = df[size_col].dropna().values.astype(float)
            if len(sizes) == 0:
                continue
            color = ds.color or None
            ax.hist(sizes, bins=bins, alpha=0.6, color=color, label=ds.display_name, edgecolor='white')
            # Mean annotation
            mean_size = np.mean(sizes)
            ax.axvline(mean_size, color=color or 'black', linestyle='--', linewidth=1)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No particle size data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Particle Size (nm)')
        ax.set_ylabel('Count')
        ax.set_title('Particle Size Distribution')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
