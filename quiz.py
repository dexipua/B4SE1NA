"""Preference quiz for undecided users: lifestyle, career, climate and values -> personal settings.

Each answer adds points to category weights, multiplies indicator weights inside a category,
and may lower the desired level of a category (modest = more accessible countries).
Points are scaled so the most important category gets weight 10. Display text lives in
i18n.TEXTS under "quiz.<question>" and "quiz.<question>.<option>".
"""

from collections.abc import Mapping
from typing import NamedTuple

from config import CATEGORIES
from settings import profile_settings

HOMICIDES, STABILITY, GDP = "WB_WDI_VC_IHR_PSRC_P5", "WB_WGI_PV_EST", "WB_WDI_NY_GDP_PCAP_PP_CD"
UNEMPLOYMENT, INFLATION = "WB_WDI_SL_UEM_TOTL_ZS", "WB_WDI_FP_CPI_TOTL_ZG"
LIFE_EXPECTANCY, HEALTH_SPENDING = "WB_WDI_SP_DYN_LE00_IN", "WB_WDI_SH_XPD_CHEX_PC_CD"

BASE_POINTS = 4  # every category starts here, so one answer cannot zero it out
MAX_WEIGHT = 10
MULT_LIMITS = (0.0, 2.0)  # same range as the fine-tuning sliders


class Option(NamedTuple):
    """Effect of one answer."""

    points: Mapping[str, int] = {}  # category -> points added to its weight
    mults: Mapping[str, float] = {}  # indicator -> factor on its weight within the category
    ideal: Mapping[str, float] = {}  # category -> desired level (the lowest across answers wins)


def everywhere(level: float) -> dict[str, float]:
    """The same desired level for every category."""
    return dict.fromkeys(CATEGORIES, level)


QUESTIONS: dict[str, dict[str, Option]] = {
    "stage": {
        "solo": Option({"economy": 2, "digital": 2}),
        "couple": Option({"economy": 2, "safety": 1}),
        "family": Option({"safety": 3, "health": 2, "environment": 1}),
        "retired": Option({"health": 3, "safety": 2, "environment": 1, "economy": -2}),
    },
    "work": {
        "job_local": Option({"economy": 3}, {UNEMPLOYMENT: 1.6}),
        "remote": Option({"digital": 4, "economy": -1}, {INFLATION: 1.4}),
        "business": Option({"governance": 3, "economy": 2}, {GDP: 1.3}),
        "none": Option({"health": 1, "economy": -2}),
    },
    "money": {
        "salary": Option({"economy": 2}, {GDP: 1.6}),
        "prices": Option({"economy": 1}, {INFLATION: 1.6}),
        "affordable": Option({"economy": 1}, ideal={"economy": 0.6}),
        "indifferent": Option({"economy": -2}),
    },
    "safety": {
        "top": Option({"safety": 4}, {HOMICIDES: 1.4}),
        "important": Option({"safety": 2}),
        "relaxed": Option({"safety": -1}),
    },
    "health": {
        "care": Option({"health": 3}, {HEALTH_SPENDING: 1.6}),
        "longevity": Option({"health": 2}, {LIFE_EXPECTANCY: 1.6}),
        "fine": Option({"health": -1}),
    },
    "climate": {
        "clean_air": Option({"environment": 4}),
        "nice": Option({"environment": 2}),
        "indifferent": Option({"environment": -1}),
    },
    "values": {
        "honesty": Option({"governance": 4}),
        "stability": Option({"safety": 2, "governance": 1}, {STABILITY: 1.6}),
        "opportunity": Option({"economy": 2, "digital": 2}),
        "wellbeing": Option({"health": 2, "environment": 2}),
    },
    "online": {
        "always": Option({"digital": 3}),
        "sometimes": Option({"digital": 1}),
        "rarely": Option({"digital": -1}),
    },
    "ambition": {
        "best": Option(),
        "balanced": Option(ideal=everywhere(0.8)),
        "modest": Option(ideal=everywhere(0.6)),
    },
}


def category_weights(chosen: list[Option]) -> dict[str, int]:
    """Points per category scaled to 0..MAX_WEIGHT, the top category getting MAX_WEIGHT."""
    points = {cat: max(BASE_POINTS + sum(o.points.get(cat, 0) for o in chosen), 0) for cat in CATEGORIES}
    top = max(max(points.values()), 1)
    return {cat: round(MAX_WEIGHT * p / top) for cat, p in points.items()}


def indicator_mults(chosen: list[Option]) -> dict[str, float]:
    """Product of every answer's factor per indicator, clipped to the slider range."""
    low, high = MULT_LIMITS
    mults: dict[str, float] = {}
    for option in chosen:
        for code, factor in option.mults.items():
            mults[code] = mults.get(code, 1.0) * factor
    return {code: round(min(max(m, low), high), 1) for code, m in mults.items()}


def desired_levels(chosen: list[Option]) -> dict[str, float]:
    """Desired level per category; when answers disagree the more modest one wins."""
    ideal: dict[str, float] = {}
    for option in chosen:
        for cat, level in option.ideal.items():
            ideal[cat] = min(ideal.get(cat, 1.0), level)
    return ideal


def quiz_settings(answers: Mapping[str, str]) -> dict[str, object]:
    """Settings (weights, multipliers, ideal, mode) from one answer per question."""
    chosen = [QUESTIONS[question][answers[question]] for question in QUESTIONS]
    return profile_settings(category_weights(chosen), desired_levels(chosen), indicator_mults(chosen))


def top_categories(settings: Mapping[str, object], n: int = 2) -> list[str]:
    """The `n` heaviest categories, ties in CATEGORIES order."""
    return sorted(CATEGORIES, key=lambda cat: -settings[cat])[:n]
