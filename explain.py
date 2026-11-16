"""Human-readable explanations built from per-indicator losses."""

import pandas as pd

from i18n import DEFAULT_LANG, label, t


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
