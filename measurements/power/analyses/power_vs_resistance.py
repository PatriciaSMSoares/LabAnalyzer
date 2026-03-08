from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() == col.lower().strip() or c.lower() in col.lower():
                return col
    return None


class PowerVsResistanceAnalysis(BaseAnalysis):
    analysis_id = 'power_vs_resistance'
    display_name = 'Power vs Resistance'

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
            r_col = _find_col(df, ['E_iR_Stack (mOhm)', 'e_ir_stack', 'hfr', 'resistance', 'rwe/ohm', 'r ('])
            p_col = _find_col(df, ['Power (Watts)', 'pwe/w', 'power', 'p (', 'p(w)'])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if r_col is None and len(num_cols) >= 1:
                r_col = num_cols[0]
            if p_col is None and len(num_cols) >= 2:
                p_col = num_cols[1]
            if r_col is None or p_col is None:
                continue
            r = df[r_col].dropna().values.astype(float)
            p = df[p_col].dropna().values.astype(float)
            n = min(len(r), len(p))
            ax.scatter(r[:n], p[:n], color=ds.color or None, label=ds.display_name,
                       s=8, alpha=0.5)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No resistance/power data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Internal Resistance (mΩ)')
        ax.set_ylabel('Power (W)')
        ax.set_title('Power vs Resistance')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
