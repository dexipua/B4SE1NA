"""Weighted distance from every country to the user's ideal profile."""

from collections import Counter

import numpy as np
import pandas as pd

from config import INDICATORS

CATEGORY_OF: dict[str, str] = {ind.code: ind.category for ind in INDICATORS}


def expand_weights(cat_weights: dict[str, float]) -> pd.Series:
    """Spread each category weight evenly over the indicators in that category."""
    counts = Counter(CATEGORY_OF.values())
    return pd.Series(
        {code: cat_weights.get(cat, 0) / counts[cat] for code, cat in CATEGORY_OF.items()},
        dtype=float,
    )


def match(X: pd.DataFrame, ideal: pd.Series, w: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    """Score countries 0-100 by weighted Euclidean distance to ideal; best first.

    Returns the score and each indicator's contribution (loss) to the squared distance.
    """
    w = w.reindex(X.columns, fill_value=0.0)
    wsum = (X.notna() * w).sum(axis=1)
    X = X[wsum > 0]
    if X.empty:
        return pd.Series(dtype=float), pd.DataFrame(columns=X.columns, dtype=float)
    wsum = wsum[X.index]
    sq = (X - ideal) ** 2 * w
    score = ((1 - np.sqrt(sq.sum(axis=1) / wsum)) * 100).sort_values(ascending=False)
    loss = sq.div(wsum, axis=0).fillna(0.0).loc[score.index]
    return score, loss


def loss_by_category(loss: pd.DataFrame) -> pd.DataFrame:
    """Sum per-indicator losses into the six categories."""
    return loss.T.groupby(CATEGORY_OF).sum().T
