"""Turn raw indicator values into comparable 0..1 scores (higher = better)."""

import numpy as np
import pandas as pd

from config import INDICATORS, INDICATOR_CODES

LOG_SCALED = {"NY.GDP.PCAP.PP.CD"}


def _scale(col: pd.Series, lower_is_better: bool) -> pd.Series:
    """Winsorize to 5-95 percentile, min-max to 0..1 and invert if needed."""
    clipped = col.clip(col.quantile(0.05), col.quantile(0.95))
    span = clipped.max() - clipped.min()
    scaled = (clipped - clipped.min()) / span if span else clipped * 0 + 0.5
    return 1 - scaled if lower_is_better else scaled


def normalize(df: pd.DataFrame, max_missing: int = 2) -> pd.DataFrame:
    """Return iso3 x indicators in 0..1, dropping countries with too many gaps."""
    X = df[INDICATOR_CODES].astype(float)
    X = X[X.isna().sum(axis=1) <= max_missing]
    X = X.apply(lambda c: np.log(c) if c.name in LOG_SCALED else c)
    return pd.DataFrame({ind.code: _scale(X[ind.code], ind.lower_is_better) for ind in INDICATORS})
