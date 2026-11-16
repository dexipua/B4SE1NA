"""Turn raw indicator values into comparable 0..1 scores (higher = better)."""

import numpy as np
import pandas as pd

from config import INDICATOR_CODES, LOG_SCALED, LOWER_IS_BETTER


def winsorize(X: pd.DataFrame, lower: float = 0.05, upper: float = 0.95) -> pd.DataFrame:
    """Clip every column to its [lower, upper] quantile range to tame outliers."""
    return X.clip(X.quantile(lower), X.quantile(upper), axis=1)


def min_max(X: pd.DataFrame) -> pd.DataFrame:
    """Scale every column to 0..1; a constant column becomes 0."""
    span = (X.max() - X.min()).replace(0, 1)
    return (X - X.min()) / span


def normalize(df: pd.DataFrame, max_missing: int = 2) -> pd.DataFrame:
    """Return an iso3 x indicator frame in 0..1 where higher is always better.

    Countries with more than `max_missing` missing indicators are dropped.
    """
    X = df[INDICATOR_CODES].astype(float)
    X = X[X.isna().sum(axis=1) <= max_missing]
    X[LOG_SCALED] = np.log(X[LOG_SCALED])
    X = min_max(winsorize(X))
    X[LOWER_IS_BETTER] = 1 - X[LOWER_IS_BETTER]
    return X
