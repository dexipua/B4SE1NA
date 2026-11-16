import pandas as pd
import requests
import csv
import time

from config import INDICATOR_CODES, INDICATORS, Indicator

BASE_URL = "https://data360api.worldbank.org/data360/data"
WGI_DB = 3


def api_code(indicator: Indicator) -> str:
    """Translate config indicator codes into Data360 INDICATOR IDs."""
    if indicator.db == WGI_DB:
        return indicator.code if indicator.code.startswith("GOV_WGI_") else f"GOV_WGI_{indicator.code}"
    normalized = indicator.code.replace(".", "_")
    return normalized if normalized.startswith("WB_WDI_") else f"WB_WDI_{normalized}"


def fetch_countries_metadata() -> pd.DataFrame:
    url = "https://api.worldbank.org/v2/countries"
    resp = requests.get(url, params={"format": "json", "per_page": 500}, timeout=30)
    resp.raise_for_status()
    payload = resp.json()[1]

    rows = [
        {
            "iso3": item["id"],
            "country": item["name"].strip(),
            "region": item["region"]["value"].strip(),
        }
        for item in payload
        if item["region"]["id"] != "NA"
    ]
    if not rows:
        return pd.DataFrame(columns=["country", "region"]).rename_axis("iso3")
    return pd.DataFrame(rows).set_index("iso3")


def fetch_indicator(
    indicator: Indicator,
    iso3_codes: list[str],
    year_from: int = 2015,
    year_to: int = 2025,
) -> pd.DataFrame:
    rows = []
    skip = 0
    params = {
        "DATABASE_ID": "WB_WGI" if indicator.db == WGI_DB else "WB_WDI",
        "INDICATOR": api_code(indicator),
        "REF_AREA": ",".join(iso3_codes),
        "timePeriodFrom": str(year_from),
        "timePeriodTo": str(year_to),
    }

    while True:
        resp = requests.get(BASE_URL, params={**params, "skip": skip}, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("value", [])
        rows.extend(batch)
        if len(rows) >= payload.get("count", 0) or not batch:
            break
        skip += 1000
        time.sleep(0.2)

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["REF_AREA", "INDICATOR", "OBS_VALUE"])

    for group in ["SEX", "AGE", "URBANISATION", "COMP_BREAKDOWN_1"]:
        if group in df.columns and df[group].notna().any():
            totals = df[df[group].isin(["_T", "_Z"])]
            if not totals.empty:
                df = totals

    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df = (
        df.dropna(subset=["OBS_VALUE"])
        .sort_values("TIME_PERIOD")
        .drop_duplicates(subset=["REF_AREA"], keep="last")
        .assign(INDICATOR=indicator.code)  # Map back to config code for pivot/reindex
    )
    return df[["REF_AREA", "INDICATOR", "OBS_VALUE"]]

def update_data():
    meta = fetch_countries_metadata()
    if meta.empty:
        return pd.DataFrame(columns=["country", "region", *INDICATOR_CODES]).rename_axis("iso3")
    
    iso3_codes = meta.index.tolist()
    raw_data = pd.concat(
        [fetch_indicator(indicator, iso3_codes) for indicator in INDICATORS],
        ignore_index=True,
    )

    if raw_data.empty:
        indicators_df = pd.DataFrame(index=meta.index, columns=INDICATOR_CODES)
    else:
        indicators_df = (
            raw_data.pivot(index="REF_AREA", columns="INDICATOR", values="OBS_VALUE")
            .reindex(columns=INDICATOR_CODES)
        )
    
    data = meta.join(indicators_df, how="inner")
    
    if not data.empty:
        data.to_csv("data/test_dataset.csv") # TODO: change path to data/dataset.csv
    return data

def load_from_csv():
    return pd.read_csv("data/test_dataset.csv") # TODO: change path to data/dataset.csv

def load_data(update: bool = False) -> pd.DataFrame | None:
    if not update:
        return load_from_csv()
    else:
        return update_data()

if __name__ == "__main__":
    data = load_data(True)
    print(data)