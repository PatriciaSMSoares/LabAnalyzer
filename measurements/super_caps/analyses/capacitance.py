from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() == col.lower().strip() or c.lower() in col.lower():
                return col
    return None


class CapacitanceAnalysis(BaseAnalysis):
    analysis_id = 'capacitance'
    display_name = 'Capacitance vs Cycle'

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

            cap_col = _find_col(df, ['capacitance charge/µf', 'capacitance discharge/µf',
                                     'capacitance', 'cap', 'f/g', 'f g', 'specific'])
            cyc_col = _find_col(df, ['cycle number', 'cycle', 'cycles'])

            if cap_col is not None and cyc_col is not None:
                x = df[cyc_col].dropna().values.astype(float)
                y = df[cap_col].dropna().values.astype(float)
                n = min(len(x), len(y))
                ax.plot(x[:n], y[:n], 'o-', color=ds.color or None,
                        label=ds.display_name, markersize=4)
                has_data = True
            else:
                # Try to compute from GCD data: C = I*dt/dV/mass
                time_col = _find_col(df, ['time/s', 'time', 't ('])
                volt_col = _find_col(df, ['ewe/v', 'ewe', 'voltage', 'v ('])
                curr_col = _find_col(df, ['i/ma', '<i>/ma', 'current', 'i ('])
                cyc2 = _find_col(df, ['cycle number', 'cycle'])
                num_cols = df.select_dtypes(include=[np.number]).columns
                if time_col is None and len(num_cols) >= 1:
                    time_col = num_cols[0]
                if volt_col is None and len(num_cols) >= 2:
                    volt_col = num_cols[1]
                if curr_col is None and len(num_cols) >= 3:
                    curr_col = num_cols[2]

                if time_col and volt_col and curr_col:
                    t = df[time_col].dropna().values.astype(float)
                    v = df[volt_col].dropna().values.astype(float)
                    i = df[curr_col].dropna().values.astype(float)
                    n = min(len(t), len(v), len(i))
                    # Simple cycle-based capacitance
                    if cyc2 is not None and n > 0:
                        cycles = df[cyc2].iloc[:n].values
                        unique = np.unique(cycles)
                        caps = []
                        cyc_nums = []
                        for c in unique[:50]:
                            mask = cycles == c
                            ti, vi, ii = t[:n][mask], v[:n][mask], i[:n][mask]
                            if len(ti) < 2:
                                continue
                            dv = np.max(vi) - np.min(vi)
                            dt = np.max(ti) - np.min(ti)
                            avg_i = np.mean(np.abs(ii))
                            if dv > 0 and dt > 0:
                                caps.append(avg_i * dt / dv)
                                cyc_nums.append(c)
                        if caps:
                            ax.plot(cyc_nums, caps, 'o-', color=ds.color or None,
                                    label=ds.display_name, markersize=4)
                            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No capacitance data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
        ax.set_xlabel('Cycle Number')
        ax.set_ylabel('Capacitance (F/g)')
        ax.set_title('Capacitance Retention vs Cycle')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        figure.tight_layout()
