"""Translations are complete and no untranslated text reaches the rendered page."""

import json
import re
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
from google.protobuf import text_format
from streamlit.testing.v1 import AppTest

from config import CATEGORIES, INDICATOR_CODES
from i18n import LANGUAGES, LOCALES_DIR, SOURCE_LANG, TEXTS, _alpha2, country_names, format_list, t
from presets import PRESETS

ROOT = Path(__file__).parent.parent
APP = str(ROOT / "app.py")
DATASETS = [ROOT / "data" / "dataset.csv", ROOT / "data" / "mock_dataset.csv"]
CYRILLIC = re.compile("[а-яіїєґА-ЯІЇЄҐ]")
PLACEHOLDER = re.compile(r"\{(\w+)\}")
NON_UK = [lang for lang in LANGUAGES if lang != "uk"]
MAX_COMPARE = 3  # app.MAX_COMPARE; app.py runs the page on import, so it is not imported here


def raw_frames() -> Iterator[pd.DataFrame]:
    """Every dataset file that exists."""
    for path in DATASETS:
        if path.exists():
            yield pd.read_csv(path, index_col="iso3", keep_default_na=False, na_values=[""])


def test_every_text_has_all_languages() -> None:
    """Each entry carries a non-empty string in every language."""
    for key, values in TEXTS.items():
        missing = [lang for lang in LANGUAGES if not values.get(lang, "").strip()]
        assert missing == [], (key, missing)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_locale_files_match_the_source(lang: str) -> None:
    """Every locale file has exactly the English keys, with the same {placeholders}."""
    source = json.loads((LOCALES_DIR / f"{SOURCE_LANG}.json").read_text(encoding="utf-8"))
    texts = json.loads((LOCALES_DIR / f"{lang}.json").read_text(encoding="utf-8"))
    assert set(texts) == set(source)
    wrong = [key for key in source if set(PLACEHOLDER.findall(texts[key])) != set(PLACEHOLDER.findall(source[key]))]
    assert wrong == []


def test_non_ukrainian_texts_have_no_cyrillic() -> None:
    """Translations are not left as copies of the Ukrainian source."""
    for key, values in TEXTS.items():
        for lang, text in values.items():
            assert lang == "uk" or not CYRILLIC.search(text), (key, lang)


def test_domain_labels_covered() -> None:
    """Categories, indicators, presets and dataset regions all have translations."""
    regions = {r for df in raw_frames() for r in df["region"].dropna()}
    keys = ([f"cat.{c}" for c in CATEGORIES] + [f"ind.{c}" for c in INDICATOR_CODES]
            + [f"preset.{p}" for p in PRESETS] + [f"region.{r}" for r in regions])
    assert [k for k in keys if k not in TEXTS] == []


def test_every_country_is_localized() -> None:
    """No country falls back to the raw (English) dataset name."""
    for df in raw_frames():
        unresolved = [c for c in df.index if f"country.{c}" not in TEXTS and _alpha2(c) is None]
        assert unresolved == []
        for lang in NON_UK:
            assert not country_names(df["country"], lang).str.contains(CYRILLIC).any()


def page_text(at: AppTest) -> str:
    """All rendered text: element protos (labels, options, markdown, charts) and table cells."""
    parts = []
    stack = [at._tree]
    while stack:
        node = stack.pop()
        stack.extend(getattr(node, "children", {}).values())
        if getattr(node, "proto", None) is not None:
            parts.append(text_format.MessageToString(node.proto, as_utf8=True))
    for df in at.dataframe:
        parts.append(df.value.reset_index().to_csv())
    return "\n".join(parts)


@pytest.mark.parametrize("lang", NON_UK)
@pytest.mark.parametrize("mode", ["best", "ideal", "similar"])
def test_no_ukrainian_left_on_page(lang: str, mode: str) -> None:
    """Every mode renders without a single Cyrillic character in another language."""
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["lang"] = lang
    at.session_state["refresh_failed"] = True
    at.run()
    at.sidebar.radio(key="mode").set_value(t(f"mode.{mode}", lang)).run()
    # Pick one more country than the compare limit allows, so its warning renders too. The
    # starting selection can hold fewer than 3 (similar mode drops the reference country).
    compare = at.multiselect(key="compare")
    ref = at.session_state["ref_country"] if mode == "similar" else None
    extras = [iso3 for iso3 in ["UKR", "POL", "DEU", "FRA", "ESP"] if iso3 not in compare.value and iso3 != ref]
    compare.set_value([*compare.value, *extras][:MAX_COMPARE + 1]).run()
    assert not at.exception
    assert at.warning, "compare-limit warning should render"
    text = page_text(at)
    for native_name in LANGUAGES.values():  # the switcher lists each language in its own script
        text = text.replace(native_name, "")
    leftovers = CYRILLIC.findall(text)
    assert leftovers == [], (lang, mode, "".join(leftovers)[:80])


def test_format_list_follows_each_language() -> None:
    """Lists of names use the language's own separators and conjunction."""
    assert format_list(["A", "B", "C"], "en") == "A, B, and C"
    assert format_list(["A", "B", "C"], "uk") == "A, B і C"
    assert format_list(["A", "B", "C"], "ja") == "A、B、C"
    assert format_list(["A"], "de") == "A"
