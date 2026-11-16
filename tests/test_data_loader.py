"""Offline tests for the World Bank loader: id mapping and response parsing."""

import pandas as pd
import pytest

import data_loader
from config import INDICATOR_CODES, INDICATORS, YEAR_COLUMNS


def test_api_code_maps_data360_ids_to_v2_ids() -> None:
    """Every configured id converts to the code the v2 API expects."""
    codes = {ind.code: data_loader.api_code(ind) for ind in INDICATORS}
    assert codes["WB_WDI_SP_DYN_LE00_IN"] == "SP.DYN.LE00.IN"
    assert codes["WB_WDI_NY_GDP_PCAP_PP_CD"] == "NY.GDP.PCAP.PP.CD"
    assert codes["WB_WGI_PV_EST"] == "GOV_WGI_PV.EST"
    assert codes["WB_WGI_CC_EST"] == "GOV_WGI_CC.EST"
    assert len(set(codes.values())) == len(INDICATORS)


def fake_api(path: str, page: int = 1, **_: object) -> object:
    """Stand-in for get_json: two economies plus an aggregate, data split over two pages."""
    if path == "country":
        return [{}, [
            {"id": "UKR", "name": "Ukraine", "region": {"id": "ECS", "value": "Europe & Central Asia "}},
            {"id": "DEU", "name": "Germany", "region": {"id": "ECS", "value": "Europe & Central Asia"}},
            {"id": "WLD", "name": "World", "region": {"id": "NA", "value": "Aggregates"}},
        ]]
    series = path.split("/")[3].split(";")
    rows = [
        {"variable": [{"concept": "Country", "id": iso3}, {"concept": "Series", "id": s},
                      {"concept": "Time", "id": "YR2024"}], "value": float(i)}
        for i, s in enumerate(series) for iso3 in ("UKR", "DEU", "WLD")
    ]
    half = len(rows) // 2 + 1
    return {"total": len(rows), "per_page": half, "source": {"data": rows[(page - 1) * half: page * half]}}


def test_download_dataset_parses_all_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    """All indicators and their years arrive; aggregates and stray spaces are gone."""
    monkeypatch.setattr(data_loader, "get_json", lambda _session, path, **p: fake_api(path, **p))
    df = data_loader.download_dataset()
    assert sorted(df.index) == ["DEU", "UKR"]
    assert list(df.columns) == ["country", "region", *INDICATOR_CODES, *YEAR_COLUMNS.values()]
    assert df[INDICATOR_CODES].notna().all().all()
    assert (df[list(YEAR_COLUMNS.values())] == 2024).all().all()
    assert df.loc["UKR", "region"] == "Europe & Central Asia"


def test_load_dataset_falls_back_to_mock(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Without a cached dataset the bundled mock data is used, years as nullable integers."""
    monkeypatch.setattr(data_loader, "DATASET_PATH", tmp_path / "missing.csv")
    df = data_loader.load_dataset()
    assert list(df.columns[2:]) == [*INDICATOR_CODES, *YEAR_COLUMNS.values()]
    assert all(isinstance(dtype, pd.Int64Dtype) for dtype in df[list(YEAR_COLUMNS.values())].dtypes)
