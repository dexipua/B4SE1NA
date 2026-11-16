"""Human-readable tables and explanations built from scores, losses and raw values."""

import pandas as pd

from config import INDICATOR_CODES, YEAR_COLUMNS
from i18n import DEFAULT_LANG, format_number, label, t

MISSING = "—"


def top_reasons(loss: pd.DataFrame, iso3: str, n: int = 3, lang: str = DEFAULT_LANG) -> list[str]:
    """Names of the indicators that pull the country furthest from the ideal."""
    worst = loss.loc[iso3].nlargest(n)
    return [label("ind", code, lang) for code, value in worst.items() if value > 0]


def why_not(loss: pd.DataFrame, iso3: str, winner_iso3: str, lang: str = DEFAULT_LANG) -> pd.DataFrame:
    """Per-indicator loss of a country vs the winner, biggest gap first, with translated headers."""
    country, leader, gap = t("col.country", lang), t("col.leader", lang), t("col.gap", lang)
    table = pd.DataFrame({country: loss.loc[iso3], leader: loss.loc[winner_iso3]})
    table[gap] = table[country] - table[leader]
    table.index = [label("ind", code, lang) for code in table.index]
    return table.rename_axis(t("col.indicator", lang)).sort_values(gap, ascending=False)


def ranking_table(score: pd.Series, names: pd.Series, regions: pd.Series,
                  lang: str = DEFAULT_LANG) -> pd.DataFrame:
    """Ranked countries (1 = best) with translated headers: iso3, country, score, region."""
    return pd.DataFrame({
        "ISO3": score.index,
        t("col.country", lang): names[score.index].to_numpy(),
        t("col.score", lang): score.round(1).to_numpy(),
        t("col.region", lang): [label("region", r, lang) for r in regions[score.index]],
    }, index=pd.RangeIndex(1, len(score) + 1, name="#"))


def format_value(row: pd.Series, code: str, lang: str) -> str:
    """One raw indicator value, locale-formatted, followed by its data year when known."""
    if pd.isna(row[code]):
        return MISSING
    text = format_number(row[code], lang)
    year = row.get(YEAR_COLUMNS[code])  # a row mixes dtypes, so the year arrives as a float
    return text if year is None or pd.isna(year) else f"{text} ({int(year)})"


def values_table(raw: pd.DataFrame, iso3s: list[str], names: pd.Series,
                 lang: str = DEFAULT_LANG) -> pd.DataFrame:
    """Actual (un-normalized) indicator values of the chosen countries, one column per country."""
    return pd.DataFrame(
        {names[iso3]: [format_value(raw.loc[iso3], code, lang) for code in INDICATOR_CODES] for iso3 in iso3s},
        index=pd.Index([label("ind", code, lang) for code in INDICATOR_CODES], name=t("col.indicator", lang)),
    )


def strengths_and_weaknesses(levels: pd.Series, raw_row: pd.Series, lang: str = DEFAULT_LANG,
                             n: int = 3) -> tuple[list[str], list[str]]:
    """The `n` indicators where a country ranks best and worst against all others.

    `levels` is the country's normalized row (0..1, higher = better); each line names the
    indicator and its actual value with year. Indicators never appear on both lists.
    """
    known = levels.dropna().sort_values(ascending=False)
    best = list(known.index[:n])
    worst = [code for code in known.index[::-1][:n] if code not in best]

    def line(code: str) -> str:
        return f"{label('ind', code, lang)}: {format_value(raw_row, code, lang)}"

    return [line(code) for code in best], [line(code) for code in worst]
