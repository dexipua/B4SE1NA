"""Download World Bank indicators from the Data360 API and cache them in data/dataset.csv.

Columns: country, region, one value column per indicator, then the year of each value.
Country names and regions come from the classic v2 API (Data360 has no country list).
"""

from collections.abc import Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from config import INDICATOR_CODES, INDICATORS, YEAR_COLUMNS, Indicator

DATA_DIR = Path(__file__).parent / "data"
DATASET_PATH = DATA_DIR / "dataset.csv"
MOCK_PATH = DATA_DIR / "mock_dataset.csv"
DATA360_URL = "https://data360api.worldbank.org/data360/data"
COUNTRIES_URL = "https://api.worldbank.org/v2/en/country"
DATABASES = {2: "WB_WDI", 3: "WB_WGI"}  # config.Indicator.db -> Data360 DATABASE_ID
# WGI publishes the estimate plus ranks, scores and standard errors; we rank on the estimate.
EXTRA_FILTERS = {3: {"COMP_BREAKDOWN_1": "WGI_EST"}}
TOTALS = {"_T", "_Z", "WGI_EST"}  # "total"/"not applicable" codes of the breakdown dimensions
BREAKDOWNS = ("SEX", "AGE", "URBANISATION", "COMP_BREAKDOWN_1")
FIRST_YEAR = 2010  # older values are stale; skipping them loses <1% of values and halves the download
AGGREGATE_REGION = "NA"  # region id the v2 API gives to World, income groups, Euro area...
TIMEOUT = 60
WORKERS = 4  # indicators downloaded in parallel


def get_json(session: requests.Session, url: str, **params: object) -> object:
    """GET one page as parsed JSON; HTTP errors raise requests exceptions."""
    resp = session.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_countries_metadata(session: requests.Session) -> pd.DataFrame:
    """Country name and region for every non-aggregate economy, indexed by iso3."""
    _, rows = get_json(session, COUNTRIES_URL, format="json", per_page=1000)
    return pd.DataFrame(
        {"iso3": r["id"], "country": r["name"].strip(), "region": r["region"]["value"].strip()}
        for r in rows if r["region"]["id"] != AGGREGATE_REGION
    ).set_index("iso3")


def fetch_rows(session: requests.Session, params: dict[str, str]) -> Iterator[dict]:
    """Every observation matching `params`, following Data360's skip-based paging."""
    skip = 0
    while True:
        body = get_json(session, DATA360_URL, **params, skip=skip)
        if not isinstance(body, dict) or "value" not in body:
            raise requests.HTTPError(f"Unexpected Data360 response: {body}")
        batch = body["value"]
        yield from batch
        skip += len(batch)
        if not batch or skip >= int(body.get("count", 0)):
            return


def fetch_indicator(session: requests.Session, indicator: Indicator, iso3s: Sequence[str]) -> pd.DataFrame:
    """Latest value since FIRST_YEAR per country: DataFrame iso3 -> value, year."""
    params = {
        "DATABASE_ID": DATABASES[indicator.db],
        "INDICATOR": indicator.code,
        "REF_AREA": ",".join(iso3s),
        "timePeriodFrom": str(FIRST_YEAR),
        **EXTRA_FILTERS.get(indicator.db, {}),
    }
    rows = pd.DataFrame(fetch_rows(session, params))
    if rows.empty:
        return pd.DataFrame(columns=["value", "year"], index=pd.Index([], name="iso3"))
    totals = pd.concat([rows[col].isin(TOTALS) for col in BREAKDOWNS if col in rows], axis=1).all(axis=1)
    return (
        rows[totals]
        .assign(value=lambda d: pd.to_numeric(d["OBS_VALUE"], errors="coerce"),
                year=lambda d: pd.to_numeric(d["TIME_PERIOD"], errors="coerce"))
        .dropna(subset=["value", "year"])
        .loc[lambda d: d["year"] >= FIRST_YEAR]  # the API does not always honour timePeriodFrom
        .sort_values("year")
        .drop_duplicates("REF_AREA", keep="last")
        .set_index("REF_AREA")
        .rename_axis("iso3")[["value", "year"]]
    )


def fetch_indicators(session: requests.Session, iso3s: Sequence[str]) -> pd.DataFrame:
    """All indicators side by side (downloaded in parallel), then the year of each value."""
    with ThreadPoolExecutor(WORKERS) as pool:
        results = dict(zip(INDICATOR_CODES, pool.map(lambda ind: fetch_indicator(session, ind, iso3s), INDICATORS)))
    values = pd.DataFrame({code: r["value"] for code, r in results.items()}).reindex(columns=INDICATOR_CODES)
    years = pd.DataFrame({YEAR_COLUMNS[code]: r["year"] for code, r in results.items()}).astype("Int64")
    return values.join(years.reindex(columns=list(YEAR_COLUMNS.values())))


def download_dataset() -> pd.DataFrame:
    """Countries joined with their indicators; economies without any data are dropped."""
    with requests.Session() as session:
        countries = fetch_countries_metadata(session)
        return countries.join(fetch_indicators(session, list(countries.index)), how="inner")


def load_dataset(refresh: bool = False) -> pd.DataFrame:
    """Return the cached dataset; download it first when `refresh` is set.

    Without a cache the bundled mock dataset is returned, so the app runs offline.
    Year columns are optional (older caches lack them) and load as nullable integers.
    """
    if refresh:
        download_dataset().to_csv(DATASET_PATH, index_label="iso3")
    path = DATASET_PATH if DATASET_PATH.exists() else MOCK_PATH
    df = pd.read_csv(path, index_col="iso3", keep_default_na=False, na_values=[""])
    return df.astype({col: "Int64" for col in YEAR_COLUMNS.values() if col in df})


def summarize(df: pd.DataFrame) -> dict[str, int | None]:
    """Countries, known values and the year span of a dataset (years are None without year columns)."""
    years = df[[col for col in YEAR_COLUMNS.values() if col in df]].stack()
    return {
        "countries": len(df),
        "values": int(df[INDICATOR_CODES].notna().sum().sum()),
        "first": int(years.min()) if len(years) else None,
        "last": int(years.max()) if len(years) else None,
    }


def main() -> None:
    """Command line: `python data_loader.py` downloads fresh data and summarises it."""
    info = summarize(load_dataset(refresh=True))
    print(f"Saved {DATASET_PATH}: {info['countries']} countries, {info['values']} values, "
          f"years {info['first']}-{info['last']}")


if __name__ == "__main__":
    main()
