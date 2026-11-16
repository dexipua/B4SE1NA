"""Rank countries by weighted Euclidean distance to an ideal profile."""

import numpy as np
import pandas as pd

from config import CATEGORIES, CATEGORY_OF


def expand_weights(cat_weights: dict[str, float]) -> pd.Series:
    """Spread each category weight evenly over the indicators in that category."""
    categories = pd.Series(CATEGORY_OF)
    per_category = categories.map(categories.value_counts())
    return categories.map(cat_weights).fillna(0.0).astype(float) / per_category


def match(X: pd.DataFrame, ideal: pd.Series, w: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    """Score countries 0-100 by closeness to `ideal`, best first.

    Returns the score and each indicator's contribution (loss) to the squared distance.
    Dimensions missing in a country or in the ideal are skipped (loss 0) and the
    remaining weights renormalized; countries with no usable weight are dropped.
    """
    w = w.reindex(X.columns).fillna(0.0)
    ideal = ideal.reindex(X.columns)
    wsum = ((X.notna() & ideal.notna()) * w).sum(axis=1)
    keep = wsum > 0
    X, wsum = X[keep], wsum[keep]
    loss = ((X - ideal) ** 2 * w).div(wsum, axis=0).fillna(0.0)
    score = ((1 - np.sqrt(loss.sum(axis=1))) * 100).sort_values(ascending=False)
    return score, loss.loc[score.index]


def similar_to(X: pd.DataFrame, iso3: str) -> tuple[pd.Series, pd.DataFrame]:
    """Rank countries by similarity to `iso3` with uniform weights, excluding it."""
    uniform = pd.Series(1.0, index=X.columns)
    return match(X.drop(index=iso3), X.loc[iso3], uniform)


def loss_by_category(loss: pd.DataFrame) -> pd.DataFrame:
    """Sum per-indicator losses into the six categories (in CATEGORIES order)."""
    return loss.T.groupby(CATEGORY_OF).sum().T.reindex(columns=list(CATEGORIES), fill_value=0.0)


def points_lost(loss: pd.DataFrame) -> pd.DataFrame:
    """Split each country's gap to a perfect score (100 - score) across indicators.

    Shares are proportional to the indicator's loss, so a row sums exactly to 100 - score
    and differences between two countries add up to their score difference.
    """
    total = np.sqrt(loss.sum(axis=1))
    return loss.mul(100 / total.where(total > 0), axis=0).fillna(0.0)
