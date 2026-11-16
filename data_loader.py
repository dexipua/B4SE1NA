"""Download World Bank indicators and cache them in data/dataset.csv."""

from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import requests

from config import INDICATOR_CODES, INDICATORS, Indicator

DATA_DIR = Path(__file__).parent / "data"
DATASET_PATH = DATA_DIR / "dataset.csv"
MOCK_PATH = DATA_DIR / "mock_dataset.csv"
API_URL = "https://api.worldbank.org/v2/en"
PAGE_SIZE = 1000
TIMEOUT = 60
WGI_DB = 3


def api_code(ind: Indicator) -> str:
    """V2 API series id for a Data360-style id.

    WB_WDI_SP_DYN_LE00_IN -> SP.DYN.LE00.IN, WB_WGI_PV_EST -> GOV_WGI_PV.EST.
    """
    dotted = ind.code.split("_", 2)[2].replace("_", ".")
    return f"GOV_WGI_{dotted}" if ind.db == WGI_DB else dotted


def get_json(session: requests.Session, path: str, **params: object) -> object:
    """GET one API page as parsed JSON; HTTP errors raise requests exceptions."""
    resp = session.get(f"{API_URL}/{path}", params={"format": "json", **params}, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_countries_metadata(session: requests.Session) -> pd.DataFrame:
    """Country name and region for every non-aggregate economy, indexed by iso3."""
    _, rows = get_json(session, "country", per_page=PAGE_SIZE)
    countries = pd.DataFrame(
        {"iso3": r["id"], "country": r["name"].strip(), "region": r["region"]["value"].strip()}
        for r in rows
    )
    return countries[countries["region"] != "Aggregates"].set_index("iso3")


def fetch_series(session: requests.Session, db: int, series: list[str]) -> Iterator[dict]:
    """Yield {country, series, value} for the most recent non-empty year, page by page."""
    path = f"sources/{db}/series/{';'.join(series)}/country/all/time/all"
    page, pages = 1, 1
    while page <= pages:
        body = get_json(session, path, mrnev=1, per_page=PAGE_SIZE, page=page)
        if not isinstance(body, dict) or "source" not in body:
            raise requests.HTTPError(f"Unexpected World Bank API response: {body}")
        pages = -(-int(body["total"]) // int(body["per_page"]))
        for row in body["source"]["data"]:
            yield {v["concept"].lower(): v["id"] for v in row["variable"]} | {"value": row["value"]}
        page += 1


def fetch_indicators(session: requests.Session) -> pd.DataFrame:
    """Most recent value of every indicator per economy (iso3 x indicator code)."""
    to_code = {api_code(ind): ind.code for ind in INDICATORS}
    rows = [
        row
        for db in sorted({ind.db for ind in INDICATORS})
        for row in fetch_series(session, db, [api_code(ind) for ind in INDICATORS if ind.db == db])
    ]
    long = pd.DataFrame(rows).assign(series=lambda d: d["series"].map(to_code))
    return long.pivot(index="country", columns="series", values="value").reindex(columns=INDICATOR_CODES)


def download_dataset() -> pd.DataFrame:
    """Countries joined with their indicators; aggregates are dropped by the join."""
    with requests.Session() as session:
        return fetch_countries_metadata(session).join(fetch_indicators(session), how="inner")


def load_dataset(refresh: bool = False) -> pd.DataFrame:
    """Return the cached dataset; download it first when `refresh` is set.

    Without a cache the bundled mock dataset is returned, so the app runs offline.
    """
    if refresh:
        download_dataset().to_csv(DATASET_PATH, index_label="iso3")
    path = DATASET_PATH if DATASET_PATH.exists() else MOCK_PATH
    return pd.read_csv(path, index_col="iso3", keep_default_na=False, na_values=[""])
