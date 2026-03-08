from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class EISBodeAnalysis(BaseAnalysis):
    analysis_id = 'eis_bode'
    display_name = 'EIS Bode'

    def render(self, datasets, config, figure, ax=None):
        figure.clear()
        ax1 = figure.add_subplot(211)
        ax2 = figure.add_subplot(212, sharex=ax1)
        has_data = False
        cfg = config if isinstance(config, dict) else {}

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            freq_col = _find_col(df, ['freq', 'frequency', 'f ('])
            zmag_col = _find_col(df, ['|z|', 'zmag', 'z_mag', 'magnitude'])
            phase_col = _find_col(df, ['phase', 'phi', 'angle'])

            num_cols = df.select_dtypes(include=[np.number]).columns
            if freq_col is None and len(num_cols) >= 1:
                freq_col = num_cols[0]
            if zmag_col is None and len(num_cols) >= 2:
                zmag_col = num_cols[1]
            if phase_col is None and len(num_cols) >= 3:
                phase_col = num_cols[2]

            if freq_col is None:
                continue

            f = df[freq_col].dropna().values.astype(float)
            color = ds.color or None

            if zmag_col is not None:
                zm = df[zmag_col].dropna().values.astype(float)
                n = min(len(f), len(zm))
                ax1.loglog(f[:n], zm[:n], '-', color=color, label=ds.display_name)

            if phase_col is not None:
                ph = df[phase_col].dropna().values.astype(float)
                n2 = min(len(f), len(ph))
                ax2.semilogx(f[:n2], ph[:n2], '-', color=color, label=ds.display_name)

            has_data = True

        if not has_data:
            ax1.text(0.5, 0.5, 'No data available', transform=ax1.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax1.set_ylabel('|Z| (Ω)')
        ax1.set_title('EIS Bode Plot')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (°)')
        if cfg.get('show_legend', True) and has_data:
            ax1.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax1.grid(True, alpha=0.3)
            ax2.grid(True, alpha=0.3)
        figure.tight_layout()
