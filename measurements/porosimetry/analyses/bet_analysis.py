from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class BETAnalysis(BaseAnalysis):
    analysis_id = 'bet'
    display_name = 'BET Analysis'

    def render(self, datasets, config, figure, ax=None):
        figure.clear()

        if not datasets or not any(ds.visible for ds in datasets):
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
            return

        n_visible = sum(1 for ds in datasets if ds.visible)
        ax_plot = figure.add_subplot(121)
        ax_table = figure.add_subplot(122)
        ax_table.axis('off')

        cfg = config if isinstance(config, dict) else {}
        table_data = []
        has_data = False

        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data

            x_col = _find_col(df, ['p/p0', 'relative pressure'])
            y_col = _find_col(df, ['qty adsorbed', 'quantity adsorbed', 'volume adsorbed', 'adsorbed'])

            num_cols = df.select_dtypes(include=[np.number]).columns
            if x_col is None and len(num_cols) >= 1:
                x_col = num_cols[0]
            if y_col is None and len(num_cols) >= 2:
                y_col = num_cols[1]

            if x_col is None or y_col is None:
                continue

            x = df[x_col].dropna().values.astype(float)
            y = df[y_col].dropna().values.astype(float)
            min_len = min(len(x), len(y))
            x = x[:min_len]
            y = y[:min_len]

            # BET linearization: P/(V*(P0-P)) vs P/P0
            # Filter range 0.05-0.35
            mask = (x > 0.05) & (x < 0.35) & (y > 0)
            if mask.sum() < 3:
                mask = (x > 0) & (x < 1) & (y > 0)

            if mask.sum() < 2:
                continue

            xm = x[mask]
            ym = y[mask]
            bet_y = xm / (ym * (1 - xm))
            bet_x = xm

            # Linear fit
            coeffs = np.polyfit(bet_x, bet_y, 1)
            slope, intercept = coeffs
            fit_y = np.polyval(coeffs, bet_x)

            color = ds.color or None
            ax_plot.scatter(bet_x, bet_y, color=color, s=20, label=ds.display_name)
            ax_plot.plot(bet_x, fit_y, '--', color=color, linewidth=1)

            # BET surface area calculation
            if slope + intercept > 0:
                Vm = 1.0 / (slope + intercept)
                C = slope / intercept + 1 if intercept != 0 else 0
                # SBET = Vm * N_A * cross_section / mass (simplified without mass)
                # Use standard: SBET = Vm * 4.353 (for N2 at 77K, per gram STP)
                sbet = Vm * 4.353
                table_data.append([ds.display_name[:20], f'{sbet:.1f}', f'{C:.1f}'])

            has_data = True

        ax_plot.set_xlabel('Relative Pressure (P/P₀)')
        ax_plot.set_ylabel('P/(V·(P₀-P)) [g/cm³]')
        ax_plot.set_title('BET Linearization')
        if cfg.get('show_legend', True) and has_data:
            ax_plot.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax_plot.grid(True, alpha=0.3)

        if table_data:
            headers = ['Sample', 'S_BET (m²/g)', 'C constant']
            tbl = ax_table.table(
                cellText=table_data,
                colLabels=headers,
                loc='center',
                cellLoc='center',
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(9)
            tbl.scale(1, 1.5)
            ax_table.set_title('BET Parameters')

        if not has_data:
            ax_plot.text(0.5, 0.5, 'No valid data for BET', transform=ax_plot.transAxes,
                        ha='center', va='center', fontsize=12, color='gray')

        figure.tight_layout()
