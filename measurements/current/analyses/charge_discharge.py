from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class ChargeDischargeAnalysis(BaseAnalysis):
    analysis_id = 'charge_discharge'
    display_name = 'Charge/Discharge'

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
            x_col = _find_col(df, ['time', 't ('])
            y_col = _find_col(df, ['current', 'i ('])
            cycle_col = _find_col(df, ['cycle'])

            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if y_col is None and len(num_cols) >= 2:
                y_col = num_cols[1]
            if x_col is None or y_col is None:
                continue

            x = df[x_col].dropna().values.astype(float)
            y = df[y_col].dropna().values.astype(float)
            n = min(len(x), len(y))
            x, y = x[:n], y[:n]
            color = ds.color or None

            if cycle_col is not None:
                cycles = df[cycle_col].iloc[:n].values
                unique_cycles = np.unique(cycles)[:5]  # plot first 5 cycles
                for cyc in unique_cycles:
                    mask = cycles == cyc
                    ax.plot(x[mask], y[mask], '-', color=color, linewidth=1,
                            label=f'{ds.display_name} C{int(cyc)}' if len(unique_cycles) > 1 else ds.display_name)
            else:
                ax.plot(x, y, '-', color=color, label=ds.display_name, linewidth=1.2)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Current (A)')
        ax.set_title('Charge/Discharge Cycles')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
