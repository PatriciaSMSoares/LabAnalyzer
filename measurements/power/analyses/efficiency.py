from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class EfficiencyAnalysis(BaseAnalysis):
    analysis_id = 'efficiency'
    display_name = 'Efficiency'

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
            # efficiency = Pout/Pin or Voltage*Current/Nominal
            x_col = _find_col(df, ['time', 't ('])
            p_out_col = _find_col(df, ['p_out', 'output power', 'pout'])
            p_in_col = _find_col(df, ['p_in', 'input power', 'pin'])

            # Fallback: compute from voltage and current
            if p_out_col is None or p_in_col is None:
                v_col = _find_col(df, ['voltage', 'volt'])
                i_col = _find_col(df, ['current', 'i ('])

            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]

            if x_col is None:
                continue

            x = df[x_col].dropna().values.astype(float)
            eff = None

            if p_out_col and p_in_col:
                po = df[p_out_col].dropna().values.astype(float)
                pi = df[p_in_col].dropna().values.astype(float)
                n = min(len(x), len(po), len(pi))
                with np.errstate(divide='ignore', invalid='ignore'):
                    eff = np.where(pi[:n] != 0, po[:n] / pi[:n] * 100, np.nan)
                x = x[:n]
            elif 'v_col' in dir() and v_col is not None and 'i_col' in dir() and i_col is not None:
                v = df[v_col].dropna().values.astype(float)
                i = df[i_col].dropna().values.astype(float)
                n = min(len(x), len(v), len(i))
                p = v[:n] * i[:n]
                p_max = np.nanmax(np.abs(p)) if len(p) > 0 else 1
                with np.errstate(divide='ignore', invalid='ignore'):
                    eff = np.where(p_max != 0, p / p_max * 100, np.nan)
                x = x[:n]

            if eff is not None:
                ax.plot(x, eff, '-', color=ds.color or None, label=ds.display_name, linewidth=1.2)
                has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No efficiency data available\n(need P_in/P_out or V/I columns)',
                    transform=ax.transAxes, ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Efficiency (%)')
        ax.set_title('Power Efficiency')
        ax.set_ylim(0, 110)
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
