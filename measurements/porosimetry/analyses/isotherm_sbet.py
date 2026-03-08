from labanalyzer.core.base_analysis import BaseAnalysis
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class IsothermSBETAnalysis(BaseAnalysis):
    analysis_id = 'isotherm_sbet'
    display_name = 'Isotherm + SBET'

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

            x_col = _find_col(df, ['p/p0', 'relative pressure', 'pressure'])
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

            if len(x) == 0:
                continue

            color = ds.color or None
            line, = ax.plot(x, y, 'o-', color=color, label=ds.display_name, markersize=4)

            # Calculate SBET
            mask = (x > 0.05) & (x < 0.35) & (y > 0)
            if mask.sum() >= 3:
                xm = x[mask]
                ym = y[mask]
                bet_y = xm / (ym * (1 - xm))
                coeffs = np.polyfit(xm, bet_y, 1)
                slope, intercept = coeffs
                if slope + intercept > 0:
                    Vm = 1.0 / (slope + intercept)
                    sbet = Vm * 4.353
                    # Annotate
                    ax.annotate(
                        f'S_BET={sbet:.0f} m²/g',
                        xy=(x[len(x)//2], y[len(y)//2]),
                        fontsize=8,
                        color=line.get_color(),
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7),
                    )
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax.set_xlabel('Relative Pressure (P/P₀)')
        ax.set_ylabel('Quantity Adsorbed (cm³/g STP)')
        ax.set_title('N₂ Isotherm with BET Surface Area')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)

        figure.tight_layout()
