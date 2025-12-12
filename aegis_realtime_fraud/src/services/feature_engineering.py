"""
Real-time Feature Engineering service.

Expose functions that transform a single transaction (dict) into numeric feature vector
matching training features.
"""
import numpy as np

FEATURE_COLUMNS = [
    "amount",
    "velocity_1h",
    "is_international",
    "card_present",
    "device_type"
]


def transform_single(txn: dict):
    """
    txn: dictionary with keys corresponding to FEATURE_COLUMNS (or convertible)
    returns: numpy array shaped (1, n_features)
    """
    vals = []
    for c in FEATURE_COLUMNS:
        v = txn.get(c, 0)
        try:
            v = float(v)
        except Exception:
            # fallback for categorical/string -> user should encode beforehand
            v = 0.0
        vals.append(v)
    return np.array(vals).reshape(1, -1)