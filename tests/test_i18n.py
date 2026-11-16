"""Translations are complete and no untranslated text reaches the rendered page."""

import re
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
from google.protobuf import text_format
from streamlit.testing.v1 import AppTest

from config import CATEGORIES, INDICATOR_CODES
from i18n import LANGUAGES, TEXTS, _alpha2, country_names, t
from presets import PRESETS

ROOT = Path(__file__).parent.parent
APP = str(ROOT / "app.py")
DATASETS = [ROOT / "data" / "dataset.csv", ROOT / "data" / "mock_dataset.csv"]
CYRILLIC = re.compile("[а-яіїєґА-ЯІЇЄҐ]")
NON_UK = [lang for lang in LANGUAGES if lang != "uk"]


def raw_frames() -> Iterator[pd.DataFrame]:
    """Every dataset file that exists."""
    for path in DATASETS:
        if path.exists():
            yield pd.read_csv(path, index_col="iso3", keep_default_na=False, na_values=[""])


def test_every_text_has_all_languages() -> None:
    """Each entry carries a non-empty string per language."""
    for key, values in TEXTS.items():
        assert len(values) == len(LANGUAGES) and all(v.strip() for v in values), key


def test_non_ukrainian_texts_have_no_cyrillic() -> None:
    """Translations are not left as copies of the Ukrainian source."""
    for key, values in TEXTS.items():
        for lang, text in zip(LANGUAGES, values):
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
    compare = at.multiselect(key="compare")
    extra = next(iso3 for iso3 in ["UKR", "POL", "DEU", "FRA"] if iso3 not in compare.value)
    compare.set_value([*compare.value, extra]).run()
    assert not at.exception
    assert at.warning, "compare-limit warning should render"
    text = page_text(at)
    for native_name in LANGUAGES.values():  # the switcher lists each language in its own script
        text = text.replace(native_name, "")
    leftovers = CYRILLIC.findall(text)
    assert leftovers == [], (lang, mode, "".join(leftovers)[:80])
