"""Offline tests for the World Bank loader: Data360 requests and response parsing."""

import pandas as pd
import pytest

import data_loader
from config import INDICATOR_CODES, INDICATORS, YEAR_COLUMNS

COUNTRIES = [
    {"id": "UKR", "name": "Ukraine", "region": {"id": "ECS", "value": "Europe & Central Asia "}},
    {"id": "DEU", "name": "Germany", "region": {"id": "ECS", "value": "Europe & Central Asia"}},
    {"id": "WLD", "name": "World", "region": {"id": "NA", "value": "Aggregates"}},
]
PAGE_SIZE = 3  # small pages so every indicator needs several requests


def observation(params: dict, iso3: str, year: int, value: float, breakdown: str) -> dict:
    """One Data360 row shaped like the real API (WGI rows carry a WGI_* breakdown)."""
    return {"REF_AREA": iso3, "INDICATOR": params["INDICATOR"], "TIME_PERIOD": str(year), "OBS_VALUE": str(value),
            "SEX": "_Z", "AGE": "_Z", "URBANISATION": "_Z", "COMP_BREAKDOWN_1": breakdown}


def fake_api(url: str, **params: object) -> object:
    """Stand-in for get_json: v2 country list, or a paged Data360 response.

    Each country has an old and a newer total value, plus a non-total row (a WGI rank
    or a female-only figure) that must be ignored.
    """
    if url == data_loader.COUNTRIES_URL:
        return [{}, COUNTRIES]
    total = "WGI_EST" if params["DATABASE_ID"] == "WB_WGI" else "_Z"
    other = "WGI_SR" if total == "WGI_EST" else "_Z"
    rows = []
    for iso3 in params["REF_AREA"].split(","):
        rows += [observation(params, iso3, 2015, 1.0, total), observation(params, iso3, 2023, 2.0, total)]
        rows.append({**observation(params, iso3, 2024, 99.0, other), "SEX": "F" if total == "_Z" else "_Z"})
    skip = int(params["skip"])
    return {"count": len(rows), "value": rows[skip: skip + PAGE_SIZE]}


@pytest.fixture
def requests_seen(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Patch the network with fake_api and record every request's parameters."""
    seen: list[dict] = []

    def fake_get_json(_session: object, url: str, **params: object) -> object:
        seen.append({"url": url, **params})
        return fake_api(url, **params)

    monkeypatch.setattr(data_loader, "get_json", fake_get_json)
    return seen


def test_every_indicator_maps_to_a_data360_database() -> None:
    """Each configured indicator belongs to a known Data360 database."""
    assert {ind.db for ind in INDICATORS} <= set(data_loader.DATABASES)


def test_download_keeps_latest_total_per_country(requests_seen: list[dict]) -> None:
    """Latest total value and its year per country; ranks, sub-groups and aggregates are dropped."""
    df = data_loader.download_dataset()
    assert sorted(df.index) == ["DEU", "UKR"]
    assert list(df.columns) == ["country", "region", *INDICATOR_CODES, *YEAR_COLUMNS.values()]
    assert (df[INDICATOR_CODES] == 2.0).all().all()
    assert (df[list(YEAR_COLUMNS.values())] == 2023).all().all()
    assert df.loc["UKR", "region"] == "Europe & Central Asia"


def test_values_before_first_year_are_dropped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Data360 may ignore timePeriodFrom, so stale years are also filtered locally."""
    params = {"INDICATOR": INDICATOR_CODES[0]}
    rows = [observation(params, "UKR", 1994, 5.0, "_Z"),  # only stale data -> no value at all
            observation(params, "DEU", 2005, 7.0, "_Z"), observation(params, "DEU", 2012, 3.0, "_Z")]
    monkeypatch.setattr(data_loader, "fetch_rows", lambda *_a, **_k: iter(rows))
    result = data_loader.fetch_indicator(None, INDICATORS[0], ["UKR", "DEU"])
    assert list(result.index) == ["DEU"]
    assert result.loc["DEU"].tolist() == [3.0, 2012]


def test_requests_filter_years_and_wgi_estimate(requests_seen: list[dict]) -> None:
    """Data360 is asked for recent years only, governance indicators for the estimate only."""
    data_loader.download_dataset()
    data360 = [r for r in requests_seen if r["url"] == data_loader.DATA360_URL]
    assert {r["INDICATOR"] for r in data360} == set(INDICATOR_CODES)
    assert all(r["timePeriodFrom"] == str(data_loader.FIRST_YEAR) for r in data360)
    assert all(r.get("COMP_BREAKDOWN_1") == "WGI_EST" for r in data360 if r["DATABASE_ID"] == "WB_WGI")
    assert {r["REF_AREA"] for r in data360} == {"UKR,DEU"}  # aggregates are never requested


def test_unexpected_response_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """An error page instead of data is reported as an HTTP error, which the app shows."""
    monkeypatch.setattr(data_loader, "get_json", lambda *_a, **_k: "<html>blocked</html>")
    with pytest.raises(data_loader.requests.HTTPError):
        list(data_loader.fetch_rows(None, {"INDICATOR": "x"}))


def test_load_dataset_falls_back_to_mock(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Without a cached dataset the bundled mock data is used, years as nullable integers."""
    monkeypatch.setattr(data_loader, "DATASET_PATH", tmp_path / "missing.csv")
    df = data_loader.load_dataset()
    assert list(df.columns[2:]) == [*INDICATOR_CODES, *YEAR_COLUMNS.values()]
    assert all(isinstance(dtype, pd.Int64Dtype) for dtype in df[list(YEAR_COLUMNS.values())].dtypes)


def test_summarize_counts_values_and_years() -> None:
    """Country count, known values and the year span; no year columns -> no span."""
    df = pd.DataFrame({code: [1.0, None] for code in INDICATOR_CODES}, index=["UKR", "DEU"])
    with_years = df.join(pd.DataFrame({col: [2012, None] for col in YEAR_COLUMNS.values()}, index=df.index))
    with_years[YEAR_COLUMNS[INDICATOR_CODES[0]]] = [2024, None]
    assert data_loader.summarize(with_years) == {"countries": 2, "values": 10, "first": 2012, "last": 2024}
    assert data_loader.summarize(df)["first"] is None
