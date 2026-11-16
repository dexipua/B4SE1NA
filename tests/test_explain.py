"""Display tables: ranking export and actual values with data years."""

import numpy as np
import pandas as pd

from config import INDICATOR_CODES, YEAR_COLUMNS
from explain import MISSING, ranking_table, values_table
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
