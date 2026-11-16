"""Quick preference quiz: light everyday scenarios -> personal settings.

Each answer adds points to category weights, multiplies indicator weights inside a category,
and may lower the desired level of a category (modest = more accessible countries).
Every category starts at BASE_POINTS and the result is scaled so the top category gets
MAX_WEIGHT. A skipped question (missing or None answer) is simply left out: it adds nothing
anywhere, so it is neutral, and skipping everything yields equal weights.
Display text lives in i18n.TEXTS under "quiz.<question>" and "quiz.<question>.<option>".
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
    """One answer: its emoji and its effect on the settings."""

    icon: str
    points: Mapping[str, int] = {}  # category -> points added to its weight
    mults: Mapping[str, float] = {}  # indicator -> factor on its weight within the category
    ideal: Mapping[str, float] = {}  # category -> desired level (the lowest across answers wins)


class Question(NamedTuple):
    """A scenario with its emoji and answer options."""

    icon: str
    options: dict[str, Option]


def everywhere(level: float) -> dict[str, float]:
    """The same desired level for every category."""
    return dict.fromkeys(CATEGORIES, level)


QUESTIONS: dict[str, Question] = {
    "weekend": Question("🌤", {
        "nature": Option("🌲", {"environment": 3}),
        "city": Option("☕", {"digital": 2, "economy": 1}),
        "family": Option("🧸", {"safety": 2, "health": 1}),
    }),
    "night": Question("🌙", {
        "calm": Option("😌", {"safety": 4}, {HOMICIDES: 1.4}),
        "alert": Option("👀", {"safety": 1}),
        "fearless": Option("🤷", {"safety": -1}),
    }),
    "wallet": Question("💳", {
        "salary": Option("💰", {"economy": 3}, {GDP: 1.5}),
        "job": Option("💼", {"economy": 3}, {UNEMPLOYMENT: 1.6}),
        "cheap": Option("🧺", {"economy": 1}, {INFLATION: 1.4}, {"economy": 0.6}),
    }),
    "doctor": Question("🩺", {
        "clinic": Option("🏥", {"health": 3}, {HEALTH_SPENDING: 1.6}),
        "prevention": Option("🥗", {"health": 2}, {LIFE_EXPECTANCY: 1.6}),
        "tea": Option("🍵", {"health": -1}),
    }),
    "paperwork": Question("📄", {
        "honest": Option("⚖", {"governance": 4}),
        "stable": Option("🧭", {"governance": 1, "safety": 1}, {STABILITY: 1.6}),
        "whatever": Option("🙃", {"governance": -1}),
    }),
    "online": Question("📱", {
        "wifi": Option("💻", {"digital": 4, "economy": -1}),
        "calls": Option("📞", {"digital": 1}),
        "offline": Option("📚", {"digital": -1}),
    }),
    "dream": Question("✨", {
        "best": Option("🏆"),
        "balanced": Option("😊", ideal=everywhere(0.8)),
        "reachable": Option("🎒", ideal=everywhere(0.6)),
    }),
}


def chosen_options(answers: Mapping[str, str | None]) -> list[Option]:
    """Options picked so far; skipped (None) and unanswered questions are left out."""
    return [QUESTIONS[q].options[a] for q, a in answers.items() if q in QUESTIONS and a is not None]


def answered_count(answers: Mapping[str, str | None]) -> int:
    """How many questions got a real answer (not skipped)."""
    return len(chosen_options(answers))


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


def quiz_settings(answers: Mapping[str, str | None]) -> dict[str, object]:
    """Settings (weights, multipliers, ideal, mode) from the answers given; skips are neutral."""
    chosen = chosen_options(answers)
    return profile_settings(category_weights(chosen), desired_levels(chosen), indicator_mults(chosen))


def top_categories(settings: Mapping[str, object], n: int = 2) -> list[str]:
    """The `n` heaviest categories, ties in CATEGORIES order."""
    return sorted(CATEGORIES, key=lambda cat: -settings[cat])[:n]
