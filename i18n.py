"""All human-readable text: UI strings, domain labels and country names in 15 languages.

Texts live in locales/<lang>.json ({key: text}), one file per language, so translators
never edit the same lines. Country names come from CLDR (Babel), number formats too.
tests/test_i18n.py fails if any language misses a key or a placeholder.
"""

import json
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
import pycountry
from babel import Locale
from babel.lists import format_list as babel_format_list
from babel.numbers import format_decimal

LOCALES_DIR = Path(__file__).parent / "locales"
LANGUAGES: dict[str, str] = {  # code -> name in that language, in switcher order
    "uk": "Українська",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "zh": "中文",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "pl": "Polski",
    "nl": "Nederlands",
    "cs": "Čeština",
    "tr": "Türkçe",
    "ja": "日本語",
    "ko": "한국어",
    "hi": "हिन्दी",
}
DEFAULT_LANG = "uk"
SOURCE_LANG = "en"  # the reference every other locale must match key for key
ALPHA2_OVERRIDES: dict[str, str] = {"XKX": "XK"}  # World Bank code -> CLDR territory


def load_locales(directory: Path = LOCALES_DIR) -> dict[str, dict[str, str]]:
    """{key: {lang: text}} from every locale file of a supported language."""
    texts: dict[str, dict[str, str]] = {}
    for lang in LANGUAGES:
        for key, text in json.loads((directory / f"{lang}.json").read_text(encoding="utf-8")).items():
            texts.setdefault(key, {})[lang] = text
    return texts


TEXTS: dict[str, dict[str, str]] = load_locales()


def t(key: str, lang: str, **fmt: object) -> str:
    """Translated text for `key`, with `{placeholders}` filled from `fmt`."""
    text = TEXTS[key][lang]
    return text.format(**fmt) if fmt else text


def label(prefix: str, name: str, lang: str) -> str:
    """Translated name of a category/indicator/preset/region; unknown regions stay as-is."""
    key = f"{prefix}.{name}"
    return t(key, lang) if key in TEXTS else name


def format_number(value: float, lang: str) -> str:
    """Locale-formatted number; fewer decimals for larger magnitudes (54 210, 74.7, -0.33)."""
    pattern = "#,##0" if abs(value) >= 100 else "#,##0.#" if abs(value) >= 10 else "#,##0.##"
    return format_decimal(value, format=pattern, locale=lang)


def format_list(items: Iterable[str], lang: str) -> str:
    """Locale-joined list: "A, B, and C" (en), "A, B і C" (uk), "A、B、C" (ja)."""
    return babel_format_list(list(items), locale=lang)


def _alpha2(iso3: str) -> str | None:
    """ISO alpha-2 code used by CLDR for a World Bank iso3 code."""
    if iso3 in ALPHA2_OVERRIDES:
        return ALPHA2_OVERRIDES[iso3]
    country = pycountry.countries.get(alpha_3=iso3)
    return country.alpha_2 if country else None


def country_names(fallback: pd.Series, lang: str) -> pd.Series:
    """Country names in `lang` (CLDR), indexed by iso3; `fallback` covers unknown codes."""
    territories = Locale.parse(lang).territories

    def name(iso3: str) -> str:
        if f"country.{iso3}" in TEXTS:
            return t(f"country.{iso3}", lang)
        return territories.get(_alpha2(iso3) or "", fallback[iso3])

    return pd.Series({iso3: name(iso3) for iso3 in fallback.index}, name="country")
