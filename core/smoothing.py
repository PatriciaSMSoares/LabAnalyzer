import numpy as np
import pandas as pd
from scipy import ndimage, signal


def apply_smoothing(y: np.ndarray, config) -> np.ndarray:
    """Apply smoothing to a 1D array based on SmoothingConfig."""
    if y is None or len(y) == 0:
        return y

    method = getattr(config, 'method', 'None')
    window = getattr(config, 'window', 5)
    sigma = getattr(config, 'sigma', 1.0)
    poly_order = getattr(config, 'poly_order', 2)

    if method == 'None' or method is None:
        return y

    y = np.asarray(y, dtype=float)

    try:
        if method == 'Moving Average':
            if window < 1:
                window = 1
            kernel = np.ones(window) / window
            # Use 'same' mode and handle edges
            smoothed = np.convolve(y, kernel, mode='same')
            # Fix edge effects by using valid convolution for center
            # and original values for edges
            half = window // 2
            result = smoothed.copy()
            # Recompute edges with smaller windows
            for i in range(half):
                w = 2 * i + 1
                result[i] = np.mean(y[:w])
                result[-(i + 1)] = np.mean(y[-(w):])
            return result

        elif method == 'EMA':
            series = pd.Series(y)
            span = max(window, 2)
            return series.ewm(span=span, adjust=True).mean().values

        elif method == 'Gaussian':
            return ndimage.gaussian_filter1d(y, sigma=sigma)

        elif method == 'Savitzky-Golay':
            wl = window if window % 2 == 1 else window + 1
            wl = max(wl, poly_order + 2)
            if len(y) >= wl:
                return signal.savgol_filter(y, wl, poly_order)
            return y

        else:
            return y

    except Exception:
        return y
