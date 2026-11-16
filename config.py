"""Indicator and category definitions shared by every module."""

from typing import NamedTuple


class Indicator(NamedTuple):
    """A World Bank indicator and how to interpret it."""

    code: str
    db: int
    category: str
    lower_is_better: bool
    label: str


CATEGORIES: dict[str, str] = {
    "safety": "Безпека",
    "economy": "Економіка",
    "health": "Здоров'я",
    "environment": "Довкілля",
    "governance": "Врядування",
    "digital": "Цифровізація",
}

INDICATORS: list[Indicator] = [
    Indicator("VC.IHR.PSRC.P5", 2, "safety", True, "Умисні вбивства на 100 тис."),
    Indicator("PV.EST", 3, "safety", False, "Політична стабільність"),
    Indicator("NY.GDP.PCAP.PP.CD", 2, "economy", False, "ВВП на душу (ПКС, $)"),
    Indicator("SL.UEM.TOTL.ZS", 2, "economy", True, "Безробіття, %"),
    Indicator("FP.CPI.TOTL.ZG", 2, "economy", True, "Інфляція, %"),
    Indicator("SP.DYN.LE00.IN", 2, "health", False, "Очікувана тривалість життя"),
    Indicator("SH.XPD.CHEX.PC.CD", 2, "health", False, "Витрати на охорону здоров'я на душу, $"),
    Indicator("EN.ATM.PM25.MC.M3", 2, "environment", True, "Забруднення повітря PM2.5"),
    Indicator("CC.EST", 3, "governance", False, "Контроль корупції"),
    Indicator("IT.NET.USER.ZS", 2, "digital", False, "Користувачі інтернету, %"),
]

INDICATOR_CODES: list[str] = [ind.code for ind in INDICATORS]
