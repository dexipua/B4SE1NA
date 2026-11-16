"""Smoke tests: the Streamlit app renders in every mode without errors."""

from pathlib import Path

import pytest
from streamlit.runtime.context import ContextProxy
from streamlit.testing.v1 import AppTest

from config import CATEGORIES
from i18n import DEFAULT_LANG, t
from presets import PRESETS
from quiz import QUESTIONS

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


def test_shared_link_restores_settings() -> None:
    """Opening a link applies its mode, weights and ideal before the first render."""
    at = AppTest.from_file(APP, default_timeout=60)
    at.query_params.update({"lang": "en", "mode": "ideal", "w": "10,0,0,0,0,0", "ideal": "0.5,1,1,1,1,1"})
    at.run()
    assert not at.exception
    assert at.session_state["lang"] == "en" and at.session_state["mode"] == "ideal"
    assert at.sidebar.slider(key="safety").value == 10
    assert at.sidebar.slider(key="ideal_safety").value == 0.5


def test_address_bar_follows_settings(app: AppTest) -> None:
    """Changing a setting rewrites the query string so the URL can be shared."""
    app.sidebar.slider(key="economy").set_value(9).run()
    assert app.query_params["w"].split(",")[1] == "9"


def test_download_and_values_table_render(app: AppTest) -> None:
    """The ranking can be downloaded and the comparison tab lists actual values."""
    assert app.get("download_button")
    assert len(app.dataframe) >= 2  # ranking + actual values of compared countries


@pytest.mark.parametrize(("host", "visible"), [("localhost:8501", True), ("demo.ngrok-free.dev", False)])
def test_refresh_only_for_local_visits(monkeypatch: pytest.MonkeyPatch, host: str, visible: bool) -> None:
    """Visitors through a public tunnel cannot trigger World Bank downloads on the host."""
    monkeypatch.setattr(ContextProxy, "headers", property(lambda _self: {"Host": host}))
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    refresh = t("refresh", DEFAULT_LANG)
    assert any(b.label == refresh for b in at.sidebar.button) == visible


def open_quiz(app: AppTest) -> None:
    """Open the quiz dialog (AppTest reruns the whole script, so it is reopened after every click)."""
    next(b for b in app.sidebar.button if b.label == t("quiz.open", DEFAULT_LANG)).click().run()


def test_quiz_cards_answer_skip_back_and_apply(app: AppTest) -> None:
    """One card per question with a progress bar; skips are allowed; the result applies the weights."""
    chosen = {"weekend": "family", "night": "calm", "doctor": "clinic"}  # everything else is skipped
    for step, question in enumerate(QUESTIONS):
        open_quiz(app)
        assert app.get("progress")[0].value == int(100 * step / len(QUESTIONS))  # AppTest reports percent
        assert app.button(key="quiz_back").disabled == (step == 0)
        target = f"quiz_{question}_{chosen[question]}" if question in chosen else "quiz_skip"
        app.button(key=target).click().run()
        assert not app.exception

    open_quiz(app)
    app.button(key="quiz_back").click().run()  # back to the last card: its skip is remembered, no answer lit
    open_quiz(app)
    assert all(b.proto.type != "primary" for b in app.button if (b.key or "").startswith("quiz_dream_"))
    app.button(key="quiz_skip").click().run()

    open_quiz(app)
    app.button(key="quiz_apply").click().run()
    assert not app.exception
    assert app.sidebar.slider(key="safety").value == 10
    assert app.success


def test_quiz_with_everything_skipped_gives_equal_weights(app: AppTest) -> None:
    """Skipping every card is allowed and yields equal weights, not an error."""
    for _ in QUESTIONS:
        open_quiz(app)
        app.button(key="quiz_skip").click().run()
    open_quiz(app)
    assert app.info  # "you skipped every question" note on the result card
    app.button(key="quiz_apply").click().run()
    assert not app.exception
    assert {app.sidebar.slider(key=cat).value for cat in CATEGORIES} == {10}


def test_explore_tab_switches_axes(app: AppTest) -> None:
    """The explore scatter starts at safety vs economy and accepts any pair of categories."""
    assert app.selectbox(key="explore_x").value == "safety"
    assert app.selectbox(key="explore_y").value == "economy"
    app.selectbox(key="explore_y").set_value("health").run()
    assert not app.exception
