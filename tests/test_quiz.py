"""Preference quiz: answers map to sensible weights and plug into the ranking."""

from pathlib import Path

import pandas as pd
import pytest

from config import CATEGORIES, INDICATOR_CODES
from i18n import TEXTS
from processing import normalize
from quiz import MAX_WEIGHT, QUESTIONS, quiz_settings, top_categories
from scoring import match
from settings import DEFAULTS, query

MOCK_CSV = Path(__file__).parent.parent / "data" / "mock_dataset.csv"


def answers(**chosen: str) -> dict[str, str]:
    """The first option of every question, with selected overrides."""
    return {question: next(iter(options)) for question, options in QUESTIONS.items()} | chosen


def test_every_effect_targets_a_known_criterion() -> None:
    """Options only touch real categories and indicators, within slider ranges."""
    for question, options in QUESTIONS.items():
        for option_id, option in options.items():
            assert set(option.points) <= set(CATEGORIES), (question, option_id)
            assert set(option.ideal) <= set(CATEGORIES), (question, option_id)
            assert set(option.mults) <= set(INDICATOR_CODES), (question, option_id)
            assert all(0 <= level <= 1 for level in option.ideal.values())


def test_every_question_and_option_is_translated() -> None:
    """Each question and answer has display text (all languages are checked in test_i18n)."""
    keys = [f"quiz.{q}" for q in QUESTIONS] + [f"quiz.{q}.{o}" for q, opts in QUESTIONS.items() for o in opts]
    assert [k for k in keys if k not in TEXTS] == []


@pytest.mark.parametrize("chosen", [
    answers(),
    answers(stage="retired", work="none", money="indifferent", safety="relaxed", online="rarely"),
    answers(stage="family", safety="top", health="care", ambition="modest"),
])
def test_settings_are_complete_and_in_range(chosen: dict[str, str]) -> None:
    """Every setting is produced, weights are 0..10 with the top one at 10, multipliers 0..2."""
    settings = quiz_settings(chosen)
    assert set(settings) == set(DEFAULTS) - {"lang"}
    weights = [settings[cat] for cat in CATEGORIES]
    assert all(0 <= w <= MAX_WEIGHT for w in weights) and max(weights) == MAX_WEIGHT
    assert all(0 <= settings[f"mult_{code}"] <= 2 for code in INDICATOR_CODES)


def test_answers_shift_priorities() -> None:
    """A safety-minded family ranks safety first; a remote worker who is always online ranks digital first."""
    family = quiz_settings(answers(stage="family", safety="top", health="care", work="none"))
    nomad = quiz_settings(answers(stage="solo", work="remote", online="always", safety="relaxed"))
    assert top_categories(family, 1) == ["safety"]
    assert top_categories(nomad, 1) == ["digital"]


def test_desired_level_is_the_most_modest_answer() -> None:
    """Ambition sets the ideal mode; 'affordable' keeps economy at 0.6 even when aiming for the best."""
    best = quiz_settings(answers(money="salary", ambition="best"))
    affordable = quiz_settings(answers(money="affordable", ambition="balanced"))
    assert best["mode"] == "best"
    assert affordable["mode"] == "ideal" and affordable["ideal_economy"] == 0.6
    assert affordable["ideal_safety"] == 0.8


def test_multipliers_compound_and_clip() -> None:
    """Two answers favouring stable prices multiply; values stay on the slider grid."""
    settings = quiz_settings(answers(work="remote", money="prices"))
    assert settings["mult_WB_WDI_FP_CPI_TOTL_ZG"] == 2.0  # 1.4 * 1.6 = 2.24, clipped


def test_quiz_settings_drive_the_ranking() -> None:
    """Quiz output feeds query() and match() and changes who ranks first."""
    X = normalize(pd.read_csv(MOCK_CSV, index_col="iso3"))
    rankings = []
    for chosen in (answers(stage="family", safety="top", climate="clean_air"),
                   answers(money="affordable", ambition="modest", safety="relaxed")):
        score, _ = match(X, *query(DEFAULTS | quiz_settings(chosen)))
        assert not score.empty and score.between(0, 100).all()
        rankings.append(list(score.index[:5]))
    assert rankings[0] != rankings[1]
