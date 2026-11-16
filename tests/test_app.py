"""Smoke tests: the Streamlit app renders in every mode without errors."""

import re
from pathlib import Path

import pytest
import streamlit as st
from streamlit.runtime.context import ContextProxy
from streamlit.testing.v1 import AppTest

from config import CATEGORIES
from data_loader import load_dataset, summarize
from i18n import DEFAULT_LANG, t
from presets import PRESETS
from quiz import QUESTIONS, quiz_settings

APP = str(Path(__file__).parent.parent / "app.py")
TOP_CARD = re.compile(r"^\d+\. ")


@pytest.fixture
def app() -> AppTest:
    """Freshly rendered app."""
    return AppTest.from_file(APP, default_timeout=60).run()



def top_cards(at: AppTest) -> list:
    """The top-5 country cards (labelled "1. Country" ...), not the profile tab's metrics."""
    return [m for m in at.metric if TOP_CARD.match(m.label)]


def test_default_mode_shows_top_five(app: AppTest) -> None:
    """The landing page ranks countries without exceptions."""
    assert not app.exception
    assert len(top_cards(app)) == 5


@pytest.mark.parametrize("mode", ["ideal", "similar"])
def test_other_modes_render(app: AppTest, mode: str) -> None:
    """Switching modes keeps the page working."""
    app.sidebar.radio(key="mode").set_value(t(f"mode.{mode}", DEFAULT_LANG)).run()
    assert not app.exception
    assert len(top_cards(app)) == 5


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


def test_country_profile_and_data_info(app: AppTest) -> None:
    """The profile tab follows the chosen country; the sidebar states how fresh the data is."""
    def rank() -> str:
        return next(m.value for m in app.metric if m.label == t("profile.rank", DEFAULT_LANG))

    ranked = len(app.selectbox(key="why_not").options) + 1  # every ranked country except the leader
    assert rank() == t("profile.rank_value", DEFAULT_LANG, rank=1, n=ranked)  # starts at the leader
    app.selectbox(key="profile_country").set_value("UKR").run()
    assert not app.exception
    assert rank() != t("profile.rank_value", DEFAULT_LANG, rank=1, n=ranked)
    assert any(m.value.startswith(f"**{t('profile.strengths', DEFAULT_LANG)}**") for m in app.markdown)
    info = summarize(load_dataset())
    assert t("data_info", DEFAULT_LANG, countries=info["countries"], first=info["first"], last=info["last"]) in [
        c.value for c in app.sidebar.caption]


# Values Streamlit hands back when a label from another language (or an older app version)
# matches no option: the raw label instead of the id. The first entry is the reported crash.
STALE_LABELS = [
    {"explore_x": "Безпека", "explore_y": "Економіка"},
    {"mode": "Схожі на країну"},
    {"mode": "similar", "ref_country": "Україна"},
    {"regions": ["Європа", "Europe & Central Asia"]},
    {"compare": ["Україна", "UKR"]},
    {"profile_country": "Україна"},
    {"why_not": "Україна"},
]


@pytest.mark.parametrize("stale", STALE_LABELS, ids=lambda stale: "+".join(stale))
def test_stale_labels_never_crash(stale: dict) -> None:
    """A leftover label in any translated widget is dropped; valid parts of a list are kept."""
    at = AppTest.from_file(APP, default_timeout=60)
    for key, value in stale.items():
        at.session_state[key] = value
    at.run()
    assert not at.exception
    assert at.session_state["explore_x"] in CATEGORIES and at.session_state["explore_y"] in CATEGORIES
    if "regions" in stale:
        assert at.session_state["regions"] == ["Europe & Central Asia"]
    if "compare" in stale:
        assert at.session_state["compare"] == ["UKR"]


def test_language_switch_keeps_choices_without_warnings(app: AppTest, caplog: pytest.LogCaptureFixture) -> None:
    """Switching language keeps every id choice and never triggers Streamlit's default/state warning."""
    app.selectbox(key="explore_y").set_value("health").run()
    app.selectbox(key="profile_country").set_value("UKR").run()
    app.multiselect(key="compare").set_value(["UKR", "POL"]).run()
    for lang in ("en", "ja", "uk"):
        app.sidebar.selectbox(key="lang").set_value(lang).run()
        assert not app.exception
        assert (app.session_state["explore_y"], app.session_state["profile_country"]) == ("health", "UKR")
        assert app.session_state["compare"] == ["UKR", "POL"]
    assert "created with a default value" not in caplog.text


def test_quiz_preview_matches_the_applied_ranking(app: AppTest) -> None:
    """The result card's "best matches" are exactly the top countries shown after applying."""
    chosen = {"weekend": "nature", "wallet": "cheap", "dream": "reachable"}
    for question in QUESTIONS:
        open_quiz(app)
        app.button(key=f"quiz_{question}_{chosen[question]}" if question in chosen else "quiz_skip").click().run()
    open_quiz(app)
    prefix = t("quiz.preview", DEFAULT_LANG, countries="").strip()
    preview = next(m.value for m in app.markdown if prefix in m.value)
    app.button(key="quiz_apply").click().run()
    top3 = [card.label.split(". ", 1)[1] for card in top_cards(app)[:3]]
    assert all(name in preview for name in top3)


def test_applying_the_quiz_reruns_the_whole_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """In the browser a click inside the dialog reruns only the dialog. Right after "apply"
    that dialog run must ask for a full app rerun, or the sidebar keeps the old sliders.

    AppTest always reruns the whole page, so this recreates the dialog's state at that moment.
    """
    calls: list[str] = []
    monkeypatch.setattr(st, "rerun", lambda *args, **kwargs: calls.append("rerun"))
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["quiz_open"] = True  # the dialog function reruns ...
    at.session_state["quiz_top"] = ["safety"]  # ... after apply_quiz stored the result
    at.run()
    assert calls == ["rerun"]


def test_quiz_result_lands_in_the_sidebar_and_closes(app: AppTest) -> None:
    """After "apply" the sliders show the quiz weights, the dialog is closed, a summary is shown."""
    chosen = {"night": "calm", "doctor": "clinic", "paperwork": "honest"}
    for question in QUESTIONS:
        open_quiz(app)
        app.button(key=f"quiz_{question}_{chosen[question]}" if question in chosen else "quiz_skip").click().run()
    open_quiz(app)
    expected = quiz_settings(chosen)
    app.button(key="quiz_apply").click().run()
    assert not app.exception
    assert {cat: app.sidebar.slider(key=cat).value for cat in CATEGORIES} == {cat: expected[cat] for cat in CATEGORIES}
    assert app.session_state["quiz_open"] is False
    assert not [b for b in app.button if (b.key or "").startswith("quiz_")]  # dialog not drawn any more
    assert app.success
    app.run()  # a later rerun must not bring the old values back
    assert app.sidebar.slider(key="health").value == expected["health"]
