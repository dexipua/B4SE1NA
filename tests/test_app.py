"""Smoke tests: the Streamlit app renders in every mode without errors."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from i18n import DEFAULT_LANG, t
from presets import PRESETS

APP = str(Path(__file__).parent.parent / "app.py")


@pytest.fixture
def app() -> AppTest:
    """Freshly rendered app."""
    return AppTest.from_file(APP, default_timeout=60).run()


def test_default_mode_shows_top_five(app: AppTest) -> None:
    """The landing page ranks countries without exceptions."""
    assert not app.exception
    assert len(app.metric) == 5


@pytest.mark.parametrize("mode", ["ideal", "similar"])
def test_other_modes_render(app: AppTest, mode: str) -> None:
    """Switching modes keeps the page working."""
    app.sidebar.radio(key="mode").set_value(t(f"mode.{mode}", DEFAULT_LANG)).run()
    assert not app.exception
    assert len(app.metric) == 5


def test_similar_mode_excludes_reference(app: AppTest) -> None:
    """The reference country never appears in its own 'similar' list."""
    app.sidebar.radio(key="mode").set_value(t("mode.similar", DEFAULT_LANG)).run()
    ref = app.sidebar.selectbox(key="ref_country").value
    assert ref not in app.selectbox(key="why_not").options


@pytest.mark.parametrize("index", range(len(PRESETS)))
def test_presets_apply(app: AppTest, index: int) -> None:
    """Each preset button loads weights and switches to the ideal mode."""
    app.sidebar.button[index].click().run()
    preset = list(PRESETS.values())[index]
    assert not app.exception
    assert app.sidebar.slider(key="safety").value == preset["weights"]["safety"]


def test_zero_weights_show_message(app: AppTest) -> None:
    """All-zero weights produce a friendly message instead of a crash."""
    for slider in app.sidebar.slider[:6]:
        slider.set_value(0)
    app.run()
    assert not app.exception
    assert app.info and not app.metric
