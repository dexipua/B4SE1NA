"""Settings: presets, the query they define, and shareable links that survive a round trip."""

import pandas as pd
import pytest

from config import CATEGORIES, CATEGORY_OF, INDICATOR_CODES
from presets import PRESETS
from settings import DEFAULTS, decode, encode, preset_settings, query

COUNTRIES = {"UKR", "POL", "DEU"}
REGIONS = {"Europe & Central Asia", "Middle East, North Africa, Afghanistan & Pakistan"}


def make_state(**overrides: object) -> dict[str, object]:
    """Default app settings with selected overrides."""
    return DEFAULTS | overrides


@pytest.mark.parametrize("preset_id", PRESETS)
def test_preset_settings_cover_every_setting(preset_id: str) -> None:
    """A preset sets all weights and ideals, resets multipliers and picks the mode."""
    settings = preset_settings(preset_id)
    assert set(settings) == set(DEFAULTS) - {"lang"}
    assert settings["mode"] == ("ideal" if PRESETS[preset_id].get("ideal") else "best")


def test_query_uses_ideal_only_in_ideal_mode() -> None:
    """Best mode aims at 1.0 everywhere; ideal mode uses the category sliders."""
    best_ideal, weights = query(make_state(ideal_safety=0.4))
    ideal_ideal, _ = query(make_state(mode="ideal", ideal_safety=0.4))
    safety = [code for code in INDICATOR_CODES if CATEGORY_OF[code] == "safety"]
    assert (best_ideal == 1).all()
    assert (ideal_ideal[safety] == 0.4).all()
    pd.testing.assert_series_equal(weights.groupby(CATEGORY_OF).sum().sort_index(),
                                   pd.Series(5.0, index=sorted(CATEGORIES)), check_names=False)


def test_round_trip_restores_every_setting() -> None:
    """Everything encoded for the ideal mode comes back unchanged."""
    state = make_state(lang="de", mode="ideal", safety=10, digital=0, ideal_economy=0.7,
                       **{f"mult_{INDICATOR_CODES[0]}": 1.5}, regions=sorted(REGIONS), complete_only=True)
    restored = decode(encode(state), COUNTRIES, REGIONS)
    assert restored == {key: state[key] for key in restored}
    assert set(restored) == set(state)


def test_only_relevant_settings_are_written() -> None:
    """Default multipliers, unused ideals and the reference country stay out of the link."""
    params = encode(make_state(ref_country="UKR"))
    assert set(params) == {"lang", "mode", "w"}
    assert encode(make_state(mode="similar", ref_country="UKR"))["ref"] == "UKR"


@pytest.mark.parametrize("params", [
    {"lang": "xx", "mode": "nope"},
    {"w": "1,2,3"},
    {"w": "1,2,3,4,5,99"},
    {"ideal": "a,b,c,d,e,f"},
    {"mult": "1,1"},
    {"ref": "ZZZ", "regions": "Atlantis", "complete": "yes"},
])
def test_invalid_params_are_dropped(params: dict[str, str]) -> None:
    """Malformed, out-of-range or unknown values never reach the session state."""
    assert decode(params, COUNTRIES, REGIONS) == {}


def test_values_snap_to_slider_steps() -> None:
    """Hand-edited numbers are rounded to what the sliders can show."""
    state = decode({"w": "1,2,3,4,5,6.4", "ideal": "0.33,1,1,1,1,1"}, COUNTRIES, REGIONS)
    assert state["digital"] == 6 and state["ideal_safety"] == 0.35
