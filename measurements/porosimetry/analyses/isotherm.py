from labanalyzer.core.base_analysis import BaseAnalysis, OptionSpec
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


class IsothermAnalysis(BaseAnalysis):
    analysis_id = 'isotherm'
    display_name = 'N₂ Isotherm'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)

        has_data = False
        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data

            x_col = _find_col(df, ['p/p0', 'relative pressure', 'p0', 'pressure'])
            y_col = _find_col(df, ['qty adsorbed', 'quantity adsorbed', 'volume adsorbed', 'adsorbed', 'qty'])

            if x_col is None:
                # Try first numeric column as x
                num_cols = df.select_dtypes(include=[np.number]).columns
                if len(num_cols) >= 2:
                    x_col = num_cols[0]
                    y_col = num_cols[1]
                elif len(num_cols) == 1:
                    x_col = num_cols[0]
                    y_col = num_cols[0]
                else:
                    continue

            if y_col is None and len(df.select_dtypes(include=[np.number]).columns) >= 2:
                y_col = df.select_dtypes(include=[np.number]).columns[1]

            if x_col is None or y_col is None:
                continue

            x = df[x_col].dropna()
            y = df[y_col].dropna()
            min_len = min(len(x), len(y))
            x = x.iloc[:min_len].values
            y = y.iloc[:min_len].values

            color = ds.color or None

            # Check for adsorption/desorption branch column
            branch_col = _find_col(df, ['branch', 'direction', 'type'])
            if branch_col is not None:
                branches = df[branch_col].iloc[:min_len]
                ads_mask = branches.str.lower().str.contains('ads', na=True)
                des_mask = ~ads_mask
                if ads_mask.any():
                    ax.plot(x[ads_mask], y[ads_mask], 'o-', color=color, label=f'{ds.display_name} (Ads)', markersize=4)
                if des_mask.any():
                    ax.plot(x[des_mask], y[des_mask], 's--', color=color, label=f'{ds.display_name} (Des)', markersize=4, alpha=0.7)
            else:
                ax.plot(x, y, 'o-', color=color, label=ds.display_name, markersize=4)
            has_data = True

        if not has_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax.set_xlabel('Relative Pressure (P/P₀)')
        ax.set_ylabel('Quantity Adsorbed (cm³/g STP)')
        ax.set_title('N₂ Adsorption/Desorption Isotherm')

        cfg = config if isinstance(config, dict) else {}
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        if cfg.get('x_log', False):
            ax.set_xscale('log')
        if cfg.get('y_log', False):
            ax.set_yscale('log')

        figure.tight_layout()
