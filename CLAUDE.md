# Country Matcher

Streamlit app that finds countries closest to a user's ideal profile using World Bank open data.
Hackathon project: Python must be the main language. UI strings are in Ukrainian.

## Core model
Each country is a vector of 10 indicators, each normalized to 0..1 (higher = better).
The user provides an IDEAL vector (default: all 1.0) and weights per indicator.
Ranking = smallest weighted Euclidean distance to the ideal. One function powers every mode.

## Architecture (one module per concern)
- config.py: INDICATORS (code, db, category, lower_is_better, label, log_scale), CATEGORIES (6);
  derived lookups INDICATOR_CODES, CATEGORY_OF, LABEL_OF, LOWER_IS_BETTER, LOG_SCALED
- data_loader.py: load_dataset(refresh=False) -> DataFrame; caches to data/dataset.csv
- processing.py: normalize(df, max_missing=2) -> DataFrame (iso3 x 10 indicators, 0..1)
- scoring.py:
  expand_weights(cat_weights: dict) -> Series  # category weight / n indicators in it
  match(X, ideal: Series, w: Series) -> (score: Series 0-100, loss: DataFrame)
  loss_by_category(loss) -> DataFrame
- explain.py: top_reasons(loss, iso3, n=3) -> list[str]; why_not(loss, iso3, winner_iso3) -> DataFrame
- charts.py: loss_bar, radar (10 axes, country vs ideal), world_map; each returns a plotly Figure, no Streamlit
- presets.py: PRESETS = {name: {"weights": {...6 categories...}, "ideal": {...optional...}}}
- app.py: Streamlit UI only; no business logic

## match() reference implementation
wsum = (X.notna() * w).sum(axis=1)
sq = (X - ideal) ** 2 * w          # NaN dims are skipped
dist = sqrt(sq.sum(axis=1) / wsum)
score = (1 - dist) * 100
loss = sq.div(wsum, axis=0)        # per-indicator contribution to the distance
If wsum == 0 for a country, drop it. If all weights are 0, return empty results.

## Modes (all use match())
1. Best country: ideal = all 1.0
2. My ideal: ideal from "desired level" sliders
3. Similar to X: ideal = X.loc[iso3], uniform weights, exclude X itself
4. Presets: weights + ideal from presets.py

## Data
Index: iso3. Columns: country, region, one per indicator.
Categories: safety, economy, health, environment, governance, digital.
Indicator ids (Data360 style, defined only in config.py; used as CSV columns everywhere):
WB_WDI_VC_IHR_PSRC_P5, WB_WGI_PV_EST (db=3), WB_WDI_NY_GDP_PCAP_PP_CD, WB_WDI_SL_UEM_TOTL_ZS,
WB_WDI_FP_CPI_TOTL_ZG, WB_WDI_SP_DYN_LE00_IN, WB_WDI_SH_XPD_CHEX_PC_CD, WB_WDI_EN_ATM_PM25_MC_M3,
WB_WGI_CC_EST (db=3), WB_WDI_IT_NET_USER_ZS.
data_loader.api_code() maps them to World Bank v2 API ids (SP.DYN.LE00.IN, GOV_WGI_PV.EST)
and downloads with plain requests (2 batched calls + country list).
Filter aggregates (World, Euro area, income groups). Most recent value per country.

## Normalization
Winsorize 5-95 percentile, log for GDP, min-max, invert lower-is-better. Do this BEFORE match().

## Rules
- Runs offline from data/dataset.csv. Network only on refresh.
- Type hints + short docstrings on every function. No dead code, no stray print().
- Small functions, no copy-paste, idiomatic pandas/numpy/plotly.
- Streamlit: preset buttons write to st.session_state via on_click; widgets use key=; use @st.cache_data.
- UI: 6 category sliders on the sidebar, per-indicator tuning inside st.expander. No custom HTML/CSS.
- Only create files listed above unless asked. Run code after each change.
- Do not commit; the human commits (each teammate commits their own work).