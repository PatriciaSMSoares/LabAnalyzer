from labanalyzer.core.base_analysis import BaseAnalysis
from labanalyzer.core.smoothing import apply_smoothing
from labanalyzer.core.data_models import SmoothingConfig
import numpy as np


def _find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None

def _identify_id_ig_peaks(x, y):
    mask_search_i_d = y[(x>1300) & (x<1380)] 
    mask_search_i_g = y[(x>1550) & (x<1600)]

    index_id = np.argmax(mask_search_i_d) if len(mask_search_i_d) > 0 else 0
    index_ig = np.argmax(mask_search_i_g) if len(mask_search_i_g) > 0 else 0

    id = mask_search_i_d[index_id] if len(mask_search_i_d) > 0 else 0
    w_id = x[(x>1300) & (x<1380)][index_id] if len(mask_search_i_d) > 0 else 0

    ig = mask_search_i_g[index_ig] if len(mask_search_i_g) > 0 else 0
    w_ig = x[(x>1550) & (x<1600)][index_ig] if len(mask_search_i_g) > 0 else 0

    return (w_id, id), (w_ig, ig)


class IdentifyIDIGPeaksAnalysis(BaseAnalysis):
    analysis_id = 'identify_id_ig_peaks'
    display_name = 'Identify ID and IG Peaks'

    def render(self, datasets, config, figure, ax=None):
        if ax is None:
            figure.clear()
            ax = figure.add_subplot(111)

        has_data = False
        cfg = config if isinstance(config, dict) else {}
        smoothing = cfg.get('smoothing', SmoothingConfig())


        for ds in datasets:
            if not ds.visible:
                continue
            df = ds.raw_data

            x_col = _find_col(df, ['wave', 'raman shift', 'wavenumber'])
            y_col = _find_col(df, ['Counts', 'kcps', 'intensity'])

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
            x, y = x[:min_len], y[:min_len]

            if len(x) < 2:
                continue

            if smoothing and smoothing.method != 'None':
                y = apply_smoothing(y, smoothing)


            (id, w_id), (ig, w_ig) = _identify_id_ig_peaks(x, y)

            ax.plot(x, y, label=f'{ds.display_name} (ID: {id:.2f}, IG: {ig:.2f})')
            ax.scatter(w_id, id, color='red', marker='o')
            ax.scatter(w_ig, ig, color='blue', marker='o')

            has_data = True


        if not has_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        ax.set_xlabel('Raman Shift (cm⁻¹)')
        ax.set_ylabel('Counts (kcps)')
        ax.set_title('Sum of All measurements')
        if cfg.get('show_legend', True) and has_data:
            ax.legend(fontsize=8)
        if cfg.get('show_grid', True):
            ax.grid(True, alpha=0.3)

        figure.tight_layout()
