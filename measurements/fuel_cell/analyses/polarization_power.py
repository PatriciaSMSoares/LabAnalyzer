from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class PolarizationPowerAnalysis(BaseAnalysis):
    analysis_id = 'polarization_power'
    display_name = 'Polarization + Power (Dual-Y)'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax1 = figure.add_subplot(111)
        else:
            ax1 = ax
        ax2 = ax1.twinx()
        has_data = False
        cfg = config if isinstance(config, dict) else {}

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data
            x_col = _find_col(df, ['current density', 'current_density', 'j ('])
            v_col = _find_col(df, ['voltage', 'volt', 'v (', 'cell voltage'])
            p_col = _find_col(df, ['power density', 'power_density', 'p (', 'power'])

            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if v_col is None and len(num_cols) >= 2:
                v_col = num_cols[1]
            if p_col is None and len(num_cols) >= 3:
                p_col = num_cols[2]

            if x_col is None:
                continue
            x = df[x_col].dropna().values.astype(float)
            color = ds.color or None

            if v_col is not None:
                y1 = df[v_col].dropna().values.astype(float)
                n = min(len(x), len(y1))
                l1, = ax1.plot(x[:n], y1[:n], 'o-', color=color, label=f'{ds.display_name} V', markersize=4)

            if p_col is not None:
                y2 = df[p_col].dropna().values.astype(float)
                n2 = min(len(x), len(y2))
                ax2.plot(x[:n2], y2[:n2], 's--', color=color, label=f'{ds.display_name} P', markersize=4, alpha=0.7)

            has_data = True

        if not has_data:
            ax1.text(0.5, 0.5, 'No data available', transform=ax1.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax1.set_xlabel('Current Density (mA/cm²)')
        ax1.set_ylabel('Voltage (V)', color='tab:blue')
        ax2.set_ylabel('Power Density (mW/cm²)', color='tab:orange')
        ax1.set_title('Polarization + Power Density')
        if cfg.get('show_grid', True):
            ax1.grid(True, alpha=0.3)

        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        if cfg.get('show_legend', True) and has_data:
            ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='upper right')

        figure.tight_layout()
