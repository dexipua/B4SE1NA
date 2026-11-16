"""Display tables: ranking export and actual values with data years."""

import numpy as np
import pandas as pd

from config import INDICATOR_CODES, YEAR_COLUMNS
from explain import MISSING, ranking_table, strengths_and_weaknesses, values_table
from i18n import format_number, label, t

GDP, INFLATION = "WB_WDI_NY_GDP_PCAP_PP_CD", "WB_WDI_FP_CPI_TOTL_ZG"


def test_ranking_table_is_ranked_and_translated() -> None:
    """Rows are numbered from 1 in score order, with translated headers and region names."""
    score = pd.Series({"DEU": 91.26, "UKR": 55.0})
    names = pd.Series({"DEU": "Germany", "UKR": "Ukraine"})
    regions = pd.Series({"DEU": "Europe & Central Asia", "UKR": "Europe & Central Asia"})
    table = ranking_table(score, names, regions, "de")
    assert list(table.index) == [1, 2]
    assert list(table.columns) == ["ISO3", t("col.country", "de"), t("col.score", "de"), t("col.region", "de")]
    assert table.iloc[0].tolist() == ["DEU", "Germany", 91.3, label("region", "Europe & Central Asia", "de")]


def test_values_table_shows_value_year_and_gaps() -> None:
    """Each cell is the locale-formatted value with its year; missing values show a dash."""
    raw = pd.DataFrame({code: [1.0] for code in INDICATOR_CODES}, index=["UKR"])
    raw[GDP], raw[INFLATION] = 18904.98, np.nan
    raw = raw.join(pd.DataFrame({col: [2024] for col in YEAR_COLUMNS.values()}, index=["UKR"]).astype("Int64"))
    table = values_table(raw, ["UKR"], pd.Series({"UKR": "Ukraine"}), "en")
    column = table["Ukraine"].set_axis(INDICATOR_CODES)
    assert column[GDP] == "18,905 (2024)"
    assert column[INFLATION] == MISSING
    assert table.index[0] == label("ind", INDICATOR_CODES[0], "en")


def test_values_table_without_year_columns() -> None:
    """Older caches without years still render plain values."""
    raw = pd.DataFrame({code: [74.692] for code in INDICATOR_CODES}, index=["UKR"])
    table = values_table(raw, ["UKR"], pd.Series({"UKR": "Україна"}), "uk")
    assert set(table["Україна"]) == {format_number(74.692, "uk")} == {"74,7"}


def test_strengths_and_weaknesses_rank_by_level() -> None:
    """Best and worst normalized levels, with actual values; missing indicators are ignored."""
    levels = pd.Series(np.linspace(1, 0, len(INDICATOR_CODES)), index=INDICATOR_CODES)
    levels[INDICATOR_CODES[1]] = np.nan
    raw = pd.Series({code: 10.0 for code in INDICATOR_CODES})
    strong, weak = strengths_and_weaknesses(levels, raw, "en", n=2)
    assert strong == [f"{label('ind', INDICATOR_CODES[0], 'en')}: 10", f"{label('ind', INDICATOR_CODES[2], 'en')}: 10"]
    assert weak[0].startswith(label("ind", INDICATOR_CODES[-1], "en"))


def test_strengths_and_weaknesses_never_overlap() -> None:
    """With few known indicators a line appears on one list only."""
    levels = pd.Series({INDICATOR_CODES[0]: 0.9, INDICATOR_CODES[1]: 0.1})
    strong, weak = strengths_and_weaknesses(levels, pd.Series({c: 1.0 for c in INDICATOR_CODES[:2]}), "en")
    assert len(strong) == 2 and weak == []
