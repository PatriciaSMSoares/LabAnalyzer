from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() == col.lower().strip() or c.lower() in col.lower():
                return col
    return None


class FlowTimeAnalysis(BaseAnalysis):
    analysis_id = 'flow_time'
    display_name = 'Flow Rate vs Time'

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
            x_col = _find_col(df, ['Time (Sec)', 'time/s', 'time', 't ('])
            anode_col = _find_col(df, ['Flow_Anode (l/min)', 'flow_anode', 'flow anode', 'anode flow'])
            cathode_col = _find_col(df, ['Flow_Cathode (l/min)', 'flow_cathode', 'flow cathode', 'cathode flow'])
            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if x_col is None:
                continue
            x = df[x_col].dropna().values.astype(float)
            color = ds.color or None
            if anode_col is not None:
                ya = df[anode_col].dropna().values.astype(float)
                n = min(len(x), len(ya))
                ax.plot(x[:n], ya[:n], '-', color=color,
                        label=f'{ds.display_name} Anode', linewidth=1.2)
                has_data = True
            if cathode_col is not None:
                yc = df[cathode_col].dropna().values.astype(float)
                n = min(len(x), len(yc))
                ax.plot(x[:n], yc[:n], '--', color=color,
                        label=f'{ds.display_name} Cathode', linewidth=1.2)
                has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No flow rate data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Flow Rate (l/min)')
        ax.set_title('Flow Rate vs Time')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
