from labanalyzer.core.base_analysis import BaseAnalysis
from math import ceil
import numpy as np
from pathlib import Path


class ImageGalleryAnalysis(BaseAnalysis):
    analysis_id = 'image_gallery'
    display_name = 'Image Gallery'

    def render(self, datasets, config, figure, ax=None):
        figure.clear()
        cfg = config if isinstance(config, dict) else {}

        visible_ds = [ds for ds in datasets if ds.visible]
        if not visible_ds:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No images loaded', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')
            ax.axis('off')
            return

        n = len(visible_ds)
        cols = min(3, n)
        rows = ceil(n / cols)

        for i, ds in enumerate(visible_ds):
            ax = figure.add_subplot(rows, cols, i + 1)
            path = Path(ds.file_path)

            if path.suffix.lower() in ['.tif', '.tiff', '.png', '.jpg', '.jpeg']:
                try:
                    from PIL import Image
                    img = Image.open(path)
                    ax.imshow(np.array(img), cmap='gray' if img.mode == 'L' else None, aspect='auto')
                    ax.set_title(ds.display_name, fontsize=8)
                    ax.axis('off')
                except Exception as e:
                    ax.text(0.5, 0.5, f'Cannot load image:\n{e}', transform=ax.transAxes,
                            ha='center', va='center', fontsize=8)
                    ax.axis('off')
            else:
                # CSV: show dataframe info
                df = ds.raw_data
                ax.text(0.5, 0.5, f'{ds.display_name}\n{df.shape[0]} rows', transform=ax.transAxes,
                        ha='center', va='center', fontsize=8)
                ax.axis('off')

        figure.suptitle('SEM Image Gallery', fontsize=10)
        figure.tight_layout()
