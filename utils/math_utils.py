import numpy as np
import pandas as pd


def compute_statistics(data: np.ndarray) -> dict:
    """Compute basic statistics on a 1D array."""
    data = np.asarray(data, dtype=float)
    data = data[~np.isnan(data)]
    if len(data) == 0:
        return {'mean': None, 'std': None, 'min': None, 'max': None, 'median': None, 'n': 0}
    return {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'median': float(np.median(data)),
        'n': len(data),
    }


def detect_columns(df: pd.DataFrame) -> dict:
    """Detect common column types in a DataFrame."""
    detected = {}
    col_lower = {col.lower(): col for col in df.columns}

    # Time
    for key in ['time', 't (s)', 'time (s)', 'time(s)']:
        if key in col_lower:
            detected['time'] = col_lower[key]
            break

    # Voltage
    for key in ['voltage', 'v (v)', 'voltage (v)', 'potential', 'e (v)']:
        if key in col_lower:
            detected['voltage'] = col_lower[key]
            break

    # Current
    for key in ['current', 'i (a)', 'current (a)', 'current (ma)']:
        if key in col_lower:
            detected['current'] = col_lower[key]
            break

    # Temperature
    for key in ['temperature', 'temp', 'temp (°c)', 'temperature (°c)']:
        if key in col_lower:
            detected['temperature'] = col_lower[key]
            break

    return detected
