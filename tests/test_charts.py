"""Chart helpers: label wrapping rules and every figure builds in every language and theme."""

from pathlib import Path

import pandas as pd
import pytest

from charts import CJK_NO_LINE_START, gap_bar, loss_bar, radar, world_map, wrap
from i18n import LANGUAGES, country_names
from processing import normalize
from scoring import loss_by_category, match, points_lost

MOCK_CSV = Path(__file__).parent.parent / "data" / "mock_dataset.csv"


def test_wrap_keeps_words_and_hyphenates_only_overflow() -> None:
    """Short words stay whole; a very long word is hyphenated, not cut silently."""
    assert wrap("Politische Stabilität", 13) == "Politische<br>Stabilität"
    assert wrap("Arbeitslosigkeit, %", 13) == "Arbeitslosig-<br>keit, %"


def test_wrap_cjk_keeps_latin_runs_and_punctuation() -> None:
    """CJK lines break by display width, never inside 'PM2.5' and never before '，'."""
    lines = wrap("空气污染（PM2.5）", 13).split("<br>") + wrap("人均卫生支出，美元", 13).split("<br>")
    assert any("PM2.5" in line for line in lines)
    assert all(line[0] not in CJK_NO_LINE_START for line in lines)


@pytest.fixture(scope="module")
def ranked() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    """Raw data, scores, points lost and the normalized matrix for the mock dataset."""
    raw = pd.read_csv(MOCK_CSV, index_col="iso3")
    X = normalize(raw)
    score, loss = match(X, pd.Series(1.0, index=X.columns), pd.Series(1.0, index=X.columns))
    return raw, score, points_lost(loss), X


@pytest.mark.parametrize("dark", [False, True])
@pytest.mark.parametrize("lang", LANGUAGES)
def test_all_figures_build(ranked: tuple, lang: str, dark: bool) -> None:
    """Every chart renders to a figure with translated, non-empty traces."""
    raw, score, lost, X = ranked
    names = country_names(raw["country"], lang)
    top = score.index[:3]
    figures = [
        loss_bar(loss_by_category(lost), names, lang, dark=dark),
        radar(X.loc[top], pd.Series(1.0, index=X.columns), names, lang, dark=dark),
        world_map(score, names, lang, dark=dark),
        gap_bar(lost.loc[top[1]] - lost.loc[top[0]], names[top[1]], names[top[0]], lang, dark=dark),
    ]
    assert all(fig.data for fig in figures)
