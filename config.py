"""Indicator and category definitions: the single source of truth for ids and semantics.

Human-readable names in every UI language live in i18n.py.
"""

from typing import NamedTuple


class Indicator(NamedTuple):
    """A World Bank indicator (Data360-style id) and how to interpret it."""

    code: str
    db: int
    category: str
    lower_is_better: bool
    log_scale: bool = False


CATEGORIES: tuple[str, ...] = ("safety", "economy", "health", "environment", "governance", "digital")
MODES: tuple[str, ...] = ("best", "ideal", "similar")

INDICATORS: list[Indicator] = [
    Indicator("WB_WDI_VC_IHR_PSRC_P5", 2, "safety", True),
    Indicator("WB_WGI_PV_EST", 3, "safety", False),
    Indicator("WB_WDI_NY_GDP_PCAP_PP_CD", 2, "economy", False, log_scale=True),
    Indicator("WB_WDI_SL_UEM_TOTL_ZS", 2, "economy", True),
    Indicator("WB_WDI_FP_CPI_TOTL_ZG", 2, "economy", True),
    Indicator("WB_WDI_SP_DYN_LE00_IN", 2, "health", False),
    Indicator("WB_WDI_SH_XPD_CHEX_PC_CD", 2, "health", False),
    Indicator("WB_WDI_EN_ATM_PM25_MC_M3", 2, "environment", True),
    Indicator("WB_WGI_CC_EST", 3, "governance", False),
    Indicator("WB_WDI_IT_NET_USER_ZS", 2, "digital", False),
]

INDICATOR_CODES: list[str] = [ind.code for ind in INDICATORS]
CATEGORY_OF: dict[str, str] = {ind.code: ind.category for ind in INDICATORS}
LOWER_IS_BETTER: list[str] = [ind.code for ind in INDICATORS if ind.lower_is_better]
LOG_SCALED: list[str] = [ind.code for ind in INDICATORS if ind.log_scale]
YEAR_COLUMNS: dict[str, str] = {code: f"{code}_year" for code in INDICATOR_CODES}  # year of each value
