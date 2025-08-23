# backend/app/utils/serialization.py
import numpy as np

try:
    import pandas as pd
except Exception:  # pandas optional
    pd = None

def to_py(obj):
    """Recursively convert numpy/pandas to plain Python types."""
    if isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if pd is not None and isinstance(obj, pd.Series):
        return {str(k): to_py(v) for k, v in obj.to_dict().items()}
    if pd is not None and isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, dict):
        return {str(k): to_py(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_py(x) for x in obj]
    return obj
