"""Preference quiz: answers map to sensible weights, skips are neutral, and results plug into the ranking."""

from pathlib import Path

import pandas as pd
import pytest

from config import CATEGORIES, INDICATOR_CODES
from i18n import TEXTS
from processing import normalize
from quiz import MAX_WEIGHT, QUESTIONS, answered_count, quiz_settings, top_categories
from scoring import match
from settings import DEFAULTS, query

MOCK_CSV = Path(__file__).parent.parent / "data" / "mock_dataset.csv"


def answers(**chosen: str | None) -> dict[str, str | None]:
    """The first option of every question, with selected overrides (None = skipped)."""
    return {q: next(iter(question.options)) for q, question in QUESTIONS.items()} | chosen


def test_every_effect_targets_a_known_criterion() -> None:
    """Options only touch real categories and indicators, within slider ranges, and have an icon."""
    for question_id, question in QUESTIONS.items():
        assert question.icon
        for option_id, option in question.options.items():
            assert option.icon, (question_id, option_id)
            assert set(option.points) <= set(CATEGORIES), (question_id, option_id)
            assert set(option.ideal) <= set(CATEGORIES), (question_id, option_id)
            assert set(option.mults) <= set(INDICATOR_CODES), (question_id, option_id)
            assert all(0 <= level <= 1 for level in option.ideal.values())


def test_every_question_and_option_is_translated() -> None:
    """Each scenario and answer has display text (all languages are checked in test_i18n)."""
    keys = [f"quiz.{q}" for q in QUESTIONS]
    keys += [f"quiz.{q}.{o}" for q, question in QUESTIONS.items() for o in question.options]
    assert [k for k in keys if k not in TEXTS] == []


@pytest.mark.parametrize("chosen", [
    answers(),
    answers(night="fearless", wallet="cheap", doctor="tea", online="offline", dream="reachable"),
    {"weekend": "family", "doctor": "clinic"},  # partly answered
    dict.fromkeys(QUESTIONS),  # everything skipped
    {},  # nothing answered at all
])
def test_settings_are_complete_and_in_range(chosen: dict[str, str | None]) -> None:
    """Every setting is produced, weights are 0..10 with the top one at 10, multipliers 0..2."""
    settings = quiz_settings(chosen)
    assert set(settings) == set(DEFAULTS) - {"lang"}
    weights = [settings[cat] for cat in CATEGORIES]
    assert all(0 <= w <= MAX_WEIGHT for w in weights) and max(weights) == MAX_WEIGHT
    assert all(0 <= settings[f"mult_{code}"] <= 2 for code in INDICATOR_CODES)


def test_skipping_everything_gives_equal_weights() -> None:
    """With no real answer every category is equally important and nothing else changes."""
    for skipped in ({}, dict.fromkeys(QUESTIONS)):
        settings = quiz_settings(skipped)
        assert {settings[cat] for cat in CATEGORIES} == {MAX_WEIGHT}
        assert settings["mode"] == "best"
        assert all(settings[f"mult_{code}"] == 1.0 for code in INDICATOR_CODES)


def test_a_skip_is_the_same_as_not_being_asked() -> None:
    """Skipping a question (None) gives exactly the result of leaving it out."""
    partial = {"night": "calm", "online": "wifi"}
    assert quiz_settings(partial | {"wallet": None, "dream": None}) == quiz_settings(partial)
    assert answered_count(partial | {"wallet": None}) == 2


def test_answers_shift_priorities() -> None:
    """A safety-minded family ranks safety first; an always-online city lover ranks digital first."""
    family = quiz_settings({"weekend": "family", "night": "calm", "online": "offline"})
    nomad = quiz_settings({"weekend": "city", "night": "fearless", "online": "wifi"})
    assert top_categories(family, 1) == ["safety"]
    assert top_categories(nomad, 1) == ["digital"]


def test_desired_level_is_the_most_modest_answer() -> None:
    """The dream answer sets the ideal mode; 'cheap' keeps economy at 0.6 even next to 'balanced'."""
    best = quiz_settings({"wallet": "salary", "dream": "best"})
    modest = quiz_settings({"wallet": "cheap", "dream": "balanced"})
    assert best["mode"] == "best"
    assert modest["mode"] == "ideal" and modest["ideal_economy"] == 0.6
    assert modest["ideal_safety"] == 0.8


def test_multipliers_apply_and_stay_on_the_slider_grid() -> None:
    """An answer's indicator factor lands in the multiplier, rounded to the slider step."""
    settings = quiz_settings({"wallet": "job", "night": "calm"})
    assert settings["mult_WB_WDI_SL_UEM_TOTL_ZS"] == 1.6
    assert settings["mult_WB_WDI_VC_IHR_PSRC_P5"] == 1.4


def test_quiz_settings_drive_the_ranking() -> None:
    """Quiz output feeds query() and match() and changes who ranks first."""
    X = normalize(pd.read_csv(MOCK_CSV, index_col="iso3"))
    rankings = []
    for chosen in ({"weekend": "nature", "night": "calm", "doctor": "clinic"},
                   {"wallet": "cheap", "dream": "reachable", "night": "fearless"}):
        score, _ = match(X, *query(DEFAULTS | quiz_settings(chosen)))
        assert not score.empty and score.between(0, 100).all()
        rankings.append(list(score.index[:5]))
    assert rankings[0] != rankings[1]
