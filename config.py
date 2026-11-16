"""Indicator and category definitions: the single source of truth for every module."""

from typing import NamedTuple


class Indicator(NamedTuple):
    """A World Bank indicator (Data360-style id) and how to interpret it."""

    code: str
    db: int
    category: str
    lower_is_better: bool
    label: str
    log_scale: bool = False


CATEGORIES: dict[str, str] = {
    "safety": "Безпека",
    "economy": "Економіка",
    "health": "Здоров'я",
    "environment": "Довкілля",
    "governance": "Врядування",
    "digital": "Цифровізація",
}

INDICATORS: list[Indicator] = [
    Indicator("WB_WDI_VC_IHR_PSRC_P5", 2, "safety", True, "Умисні вбивства на 100 тис."),
    Indicator("WB_WGI_PV_EST", 3, "safety", False, "Політична стабільність"),
    Indicator("WB_WDI_NY_GDP_PCAP_PP_CD", 2, "economy", False, "ВВП на душу (ПКС, $)", log_scale=True),
    Indicator("WB_WDI_SL_UEM_TOTL_ZS", 2, "economy", True, "Безробіття, %"),
    Indicator("WB_WDI_FP_CPI_TOTL_ZG", 2, "economy", True, "Інфляція, %"),
    Indicator("WB_WDI_SP_DYN_LE00_IN", 2, "health", False, "Очікувана тривалість життя"),
    Indicator("WB_WDI_SH_XPD_CHEX_PC_CD", 2, "health", False, "Витрати на охорону здоров'я на душу, $"),
    Indicator("WB_WDI_EN_ATM_PM25_MC_M3", 2, "environment", True, "Забруднення повітря PM2.5"),
    Indicator("WB_WGI_CC_EST", 3, "governance", False, "Контроль корупції"),
    Indicator("WB_WDI_IT_NET_USER_ZS", 2, "digital", False, "Користувачі інтернету, %"),
]

INDICATOR_CODES: list[str] = [ind.code for ind in INDICATORS]
CATEGORY_OF: dict[str, str] = {ind.code: ind.category for ind in INDICATORS}
LABEL_OF: dict[str, str] = {ind.code: ind.label for ind in INDICATORS}
LOWER_IS_BETTER: list[str] = [ind.code for ind in INDICATORS if ind.lower_is_better]
LOG_SCALED: list[str] = [ind.code for ind in INDICATORS if ind.log_scale]
