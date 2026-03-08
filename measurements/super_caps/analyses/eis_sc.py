from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() == col.lower().strip() or c.lower() in col.lower():
                return col
    return None


class EISSCAnalysis(BaseAnalysis):
    analysis_id = 'eis_sc'
    display_name = 'EIS (Supercapacitor)'

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
            zr_col = _find_col(df, ["re(z/ohm)", "re(z)", "z'", "zreal", "z_real", "real"])
            zi_col = _find_col(df, ["-im(z/ohm)", "im(z/ohm)", "-im(z)", "im(z)", "-z''", "zimag", "z_imag", "imag"])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if zr_col is None and len(num_cols) >= 1:
                zr_col = num_cols[0]
            if zi_col is None and len(num_cols) >= 2:
                zi_col = num_cols[1]
            if zr_col is None or zi_col is None:
                continue
            zr = df[zr_col].dropna().values.astype(float)
            zi = df[zi_col].dropna().values.astype(float)
            n = min(len(zr), len(zi))
            ax.plot(zr[:n], -zi[:n], 'o-', color=ds.color or None, label=ds.display_name, markersize=4)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No EIS data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlabel("Z' (Ω)")
        ax.set_ylabel("-Z'' (Ω)")
        ax.set_title('EIS Nyquist (Supercapacitor)')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
