from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() == col.lower().strip() or c.lower() in col.lower():
                return col
    return None


class AnodeVsCathodeRHAnalysis(BaseAnalysis):
    analysis_id = 'anode_vs_cathode_rh'
    display_name = 'Anode vs Cathode RH'

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
            x_col = _find_col(df, ['RH_Anode (%)', 'rh_anode', 'rh anode', 'anode rh'])
            y_col = _find_col(df, ['RH_Cathode (%)', 'rh_cathode', 'rh cathode', 'cathode rh'])
            if x_col is None or y_col is None:
                continue
            x = df[x_col].dropna().values.astype(float)
            y = df[y_col].dropna().values.astype(float)
            n = min(len(x), len(y))
            ax.scatter(x[:n], y[:n], color=ds.color or None, label=ds.display_name,
                       s=10, alpha=0.6)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No RH data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Anode RH (%)')
        ax.set_ylabel('Cathode RH (%)')
        ax.set_title('Anode vs Cathode Relative Humidity')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
