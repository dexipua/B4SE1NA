"""User settings as plain data: defaults, presets, the query they define, and shareable links.

Keys mirror st.session_state: lang, mode, the 6 category weights, ideal_<cat>, mult_<code>,
ref_country, regions, complete_only. No Streamlit here, so everything is unit-testable.
"""

from collections.abc import Collection, Mapping

import pandas as pd

from config import CATEGORIES, INDICATORS, INDICATOR_CODES, MODES
from i18n import DEFAULT_LANG, LANGUAGES
from presets import PRESETS
from scoring import expand_weights

MODE_BEST, MODE_IDEAL, MODE_SIMILAR = MODES
DEFAULTS: dict[str, object] = {
    "lang": DEFAULT_LANG,
    "mode": MODE_BEST,
    **{cat: 5 for cat in CATEGORIES},
    **{f"ideal_{cat}": 1.0 for cat in CATEGORIES},
    **{f"mult_{code}": 1.0 for code in INDICATOR_CODES},
}
LIST_SEP = ","
REGION_SEP = "|"  # region names contain commas
WEIGHT_RANGE, IDEAL_RANGE, MULT_RANGE = (0, 10, 1), (0.0, 1.0, 0.05), (0.0, 2.0, 0.1)


def profile_settings(weights: Mapping[str, float], ideal: Mapping[str, float] | None = None,
                     mults: Mapping[str, float] | None = None) -> dict[str, object]:
    """Full settings for a profile: missing weights are 0, ideals 1.0, multipliers 1.0.

    The mode is "ideal" when any desired level is given, otherwise "best".
    """
    ideal, mults = ideal or {}, mults or {}
    return {
        **{cat: weights.get(cat, 0) for cat in CATEGORIES},
        **{f"ideal_{cat}": ideal.get(cat, 1.0) for cat in CATEGORIES},
        **{f"mult_{code}": mults.get(code, 1.0) for code in INDICATOR_CODES},
        "mode": MODE_IDEAL if ideal else MODE_BEST,
    }


def preset_settings(preset_id: str) -> dict[str, object]:
    """Weights, ideal and mode of a preset; indicator multipliers reset to 1."""
    preset = PRESETS[preset_id]
    return profile_settings(preset["weights"], preset.get("ideal"))


def query(settings: Mapping[str, object]) -> tuple[pd.Series, pd.Series]:
    """Ideal profile and per-indicator weights for the best/ideal modes."""
    mults = pd.Series({code: settings[f"mult_{code}"] for code in INDICATOR_CODES})
    weights = expand_weights({cat: settings[cat] for cat in CATEGORIES}) * mults
    if settings["mode"] == MODE_IDEAL:
        ideal = pd.Series({ind.code: settings[f"ideal_{ind.category}"] for ind in INDICATORS})
    else:
        ideal = pd.Series(1.0, index=INDICATOR_CODES)
    return ideal, weights


def _join(values: list[float]) -> str:
    """Compact comma-separated numbers (1, 0.7, 0.05)."""
    return LIST_SEP.join(f"{v:g}" for v in values)


def _parse(text: str, count: int, bounds: tuple[float, float, float]) -> list[float] | None:
    """`count` numbers within bounds, snapped to the slider step; None if malformed."""
    low, high, step = bounds
    try:
        values = [float(v) for v in text.split(LIST_SEP)]
    except ValueError:
        return None
    if len(values) != count or not all(low <= v <= high for v in values):
        return None
    return [round(round(v / step) * step, 2) for v in values]


def encode(settings: Mapping[str, object]) -> dict[str, str]:
    """Query parameters for a shareable link; only what matters for the mode is written."""
    mode = settings["mode"]
    params = {"lang": settings["lang"], "mode": mode, "w": _join([settings[cat] for cat in CATEGORIES])}
    if mode == MODE_IDEAL:
        params["ideal"] = _join([settings[f"ideal_{cat}"] for cat in CATEGORIES])
    mults = [settings[f"mult_{code}"] for code in INDICATOR_CODES]
    if any(m != 1 for m in mults):
        params["mult"] = _join(mults)
    if mode == MODE_SIMILAR and settings.get("ref_country"):
        params["ref"] = settings["ref_country"]
    if settings.get("regions"):
        params["regions"] = REGION_SEP.join(settings["regions"])
    if settings.get("complete_only"):
        params["complete"] = "1"
    return params


def decode(params: Mapping[str, str], countries: Collection[str],
           regions: Collection[str]) -> dict[str, object]:
    """Settings from query parameters; invalid or unknown parts are skipped, so a bad link is harmless."""
    settings: dict[str, object] = {}
    if params.get("lang") in LANGUAGES:
        settings["lang"] = params["lang"]
    if params.get("mode") in MODES:
        settings["mode"] = params["mode"]
    if weights := _parse(params.get("w", ""), len(CATEGORIES), WEIGHT_RANGE):
        settings |= {cat: int(w) for cat, w in zip(CATEGORIES, weights)}
    if ideal := _parse(params.get("ideal", ""), len(CATEGORIES), IDEAL_RANGE):
        settings |= {f"ideal_{cat}": v for cat, v in zip(CATEGORIES, ideal)}
    if mults := _parse(params.get("mult", ""), len(INDICATOR_CODES), MULT_RANGE):
        settings |= {f"mult_{code}": m for code, m in zip(INDICATOR_CODES, mults)}
    if params.get("ref") in countries:
        settings["ref_country"] = params["ref"]
    if chosen := [r for r in params.get("regions", "").split(REGION_SEP) if r in regions]:
        settings["regions"] = chosen
    if params.get("complete") == "1":
        settings["complete_only"] = True
    return settings
