'''
"""Download World Bank indicators and cache them in data/dataset.csv."""

from pathlib import Path

import pandas as pd
import wbgapi as wb

from config import INDICATOR_CODES, INDICATORS, Indicator

DATA_DIR = Path(__file__).parent / "data"
DATASET_PATH = DATA_DIR / "dataset.csv"
MOCK_PATH = DATA_DIR / "mock_dataset.csv"
WGI_DB = 3


def api_code(ind: Indicator) -> str:
    """Series id as the API expects it (WGI series carry a GOV_WGI_ prefix)."""
    return f"GOV_WGI_{ind.code}" if ind.db == WGI_DB else ind.code


def fetch_indicators() -> pd.DataFrame:
    """Most recent non-empty value of every indicator per economy (iso3 x code)."""
    to_code = {api_code(ind): ind.code for ind in INDICATORS}
    rows = [
        row
        for db in sorted({ind.db for ind in INDICATORS})
        for row in wb.data.fetch(
            [api_code(ind) for ind in INDICATORS if ind.db == db],
            economy="all", mrnev=1, db=db, skipAggs=True,
        )
    ]
    long = pd.DataFrame(rows).assign(series=lambda d: d["series"].map(to_code))
    return long.pivot(index="economy", columns="series", values="value").reindex(columns=INDICATOR_CODES)


def fetch_countries() -> pd.DataFrame:
    """Country name and region name for every non-aggregate economy, indexed by iso3."""
    region_names = {r["code"]: r["name"] for r in wb.region.list()}
    eco = wb.economy.DataFrame(skipAggs=True)
    return pd.DataFrame({
        "country": eco["name"].str.strip(),
        "region": eco["region"].map(region_names).str.strip(),
    }).rename_axis("iso3")


def load_dataset(refresh: bool = False) -> pd.DataFrame:
    """Return the cached dataset; download it first when `refresh` is set.

    Without a cache the bundled mock dataset is returned, so the app runs offline.
    """
    if refresh:
        fetch_countries().join(fetch_indicators(), how="inner").to_csv(DATASET_PATH)
    path = DATASET_PATH if DATASET_PATH.exists() else MOCK_PATH
    return pd.read_csv(path, index_col="iso3", keep_default_na=False, na_values=[""])
'''


from config import Indicator, INDICATORS
import pandas as pd
import requests

def fetch_countries_metadata() -> pd.DataFrame:
    url = "https://api.worldbank.org/v2/countries"
    params={
        "format" : "json",
        "per_page" : 500
    }
    resp = requests.get(url, params=params)
    print(resp.json()[1])

def fetch_indicator(indicator : Indicator, ):
    pass

fetch_countries_metadata()
