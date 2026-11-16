"""Tests for normalization and the match() scoring core."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from config import CATEGORIES, INDICATOR_CODES, LOWER_IS_BETTER
from processing import min_max, normalize
from scoring import expand_weights, loss_by_category, match, similar_to

MOCK_CSV = Path(__file__).parent.parent / "data" / "mock_dataset.csv"


@pytest.fixture(scope="module")
def raw() -> pd.DataFrame:
    """Raw mock dataset indexed by iso3."""
    return pd.read_csv(MOCK_CSV, index_col="iso3")


@pytest.fixture(scope="module")
def X(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalized mock dataset."""
    return normalize(raw)


@pytest.fixture
def uniform() -> pd.Series:
    """Equal weight on every indicator."""
    return pd.Series(1.0, index=INDICATOR_CODES)


def test_normalize_shape_and_range(raw: pd.DataFrame, X: pd.DataFrame) -> None:
    """Output is iso3 x 10 indicators within 0..1; too-sparse rows are dropped."""
    assert list(X.columns) == INDICATOR_CODES
    assert ((X >= 0) & (X <= 1) | X.isna()).all().all()
    assert "IND" in raw.index and "IND" not in X.index


def test_min_max_constant_column_and_nan() -> None:
    """A constant column maps to 0.5 and missing values stay missing."""
    X = pd.DataFrame({"flat": [3.0, 3.0, np.nan], "ramp": [0.0, 5.0, 10.0]})
    out = min_max(X)
    assert out["flat"].iloc[:2].tolist() == [0.5, 0.5] and np.isnan(out["flat"].iloc[2])
    assert out["ramp"].tolist() == [0.0, 0.5, 1.0]


def test_all_zero_weights_returns_empty(X: pd.DataFrame) -> None:
    """With every weight at 0 no country can be ranked."""
    w = expand_weights({c: 0 for c in CATEGORIES})
    score, loss = match(X, pd.Series(1.0, index=X.columns), w)
    assert score.empty and loss.empty


def test_country_vs_own_vector_scores_100(X: pd.DataFrame, uniform: pd.Series) -> None:
    """A country compared with its own profile is a perfect match."""
    score, loss = match(X, X.loc["DEU"], uniform)
    assert score["DEU"] == pytest.approx(100)
    assert score.index[0] == "DEU"
    assert loss.loc["DEU"].sum() == pytest.approx(0)


@pytest.mark.parametrize("code", LOWER_IS_BETTER)
def test_lower_is_better_inverted(raw: pd.DataFrame, X: pd.DataFrame, code: str) -> None:
    """The lowest raw value maps to 1 and the highest to 0."""
    col = raw.loc[X.index, code]
    assert X.loc[col.idxmin(), code] == pytest.approx(1)
    assert X.loc[col.idxmax(), code] == pytest.approx(0)


def test_nan_dims_skipped_and_weights_renormalized() -> None:
    """Missing dimensions are ignored; a country with nothing usable is dropped."""
    X = pd.DataFrame(
        {"a": [0.5, 0.5, np.nan], "b": [np.nan, 1.0, 1.0], "c": [1.0, 1.0, np.nan]},
        index=["HAS_NAN", "FULL", "ONLY_B"],
    )
    ideal = pd.Series(1.0, index=X.columns)
    w = pd.Series({"a": 1.0, "b": 0.0, "c": 1.0})
    score, loss = match(X, ideal, w)
    expected = (1 - np.sqrt(0.25 / 2)) * 100
    assert score["HAS_NAN"] == pytest.approx(expected)
    assert score["FULL"] == pytest.approx(expected)
    assert "ONLY_B" not in score.index
    assert loss.loc["HAS_NAN"].sum() == pytest.approx(0.125)


def test_similar_to_excludes_reference(X: pd.DataFrame) -> None:
    """'Similar to X' never recommends X itself."""
    score, loss = similar_to(X, "POL")
    assert "POL" not in score.index
    assert len(score) == len(X) - 1
    assert list(loss.index) == list(score.index)


def test_expand_weights_splits_category_evenly() -> None:
    """Category weight is divided among its indicators."""
    w = expand_weights({"economy": 6, "digital": 3})
    assert w["NY.GDP.PCAP.PP.CD"] == pytest.approx(2)
    assert w["IT.NET.USER.ZS"] == pytest.approx(3)
    assert w["PV.EST"] == 0


def test_loss_by_category_sums_to_total(X: pd.DataFrame, uniform: pd.Series) -> None:
    """Category losses add up to the per-country total loss."""
    _, loss = match(X, pd.Series(1.0, index=X.columns), uniform)
    by_cat = loss_by_category(loss)
    assert list(by_cat.columns) == list(CATEGORIES)
    pd.testing.assert_series_equal(by_cat.sum(axis=1), loss.sum(axis=1))
