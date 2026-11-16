"""Human-readable explanations built from per-indicator losses."""

import pandas as pd

from config import INDICATORS

LABEL_OF: dict[str, str] = {ind.code: ind.label for ind in INDICATORS}


def top_reasons(loss: pd.DataFrame, iso3: str, n: int = 3) -> list[str]:
    """Indicators that pull the country furthest from the ideal."""
    worst = loss.loc[iso3].nlargest(n)
    return [LABEL_OF[code] for code, value in worst.items() if value > 0]


def why_not(loss: pd.DataFrame, iso3: str, winner_iso3: str) -> pd.DataFrame:
    """Per-indicator loss of a country vs the winner, biggest gap first."""
    table = pd.DataFrame({"Країна": loss.loc[iso3], "Лідер": loss.loc[winner_iso3]})
    table["Різниця"] = table["Країна"] - table["Лідер"]
    return table.rename(index=LABEL_OF).sort_values("Різниця", ascending=False)
