"""Streamlit UI for Country Matcher; all logic lives in the other modules."""

import pandas as pd
import requests
import streamlit as st

from charts import gap_bar, loss_bar, radar, world_map
from config import CATEGORIES, INDICATORS, INDICATOR_CODES
from data_loader import DATASET_PATH, load_dataset
from explain import top_reasons, why_not
from i18n import DEFAULT_LANG, LANGUAGES, country_names, label, t
from presets import PRESETS
from processing import normalize
from scoring import expand_weights, loss_by_category, match, points_lost, similar_to

MODE_BEST, MODE_IDEAL, MODE_SIMILAR = "best", "ideal", "similar"
MAX_COMPARE = 3
CARD_WIDTH = "stretch"  # cards share the row and wrap on narrow screens
COUNTRY_WIDGETS = ("ref_country", "compare", "why_not", "regions")
TABLE_HEIGHT = 386  # px: ten rows plus the header, no half-visible row
PLOTLY_CONFIG = {"displayModeBar": False}  # plotly's modebar tooltips are English-only
DEFAULTS: dict[str, object] = {
    "lang": DEFAULT_LANG,
    "mode": MODE_BEST,
    **{cat: 5 for cat in CATEGORIES},
    **{f"ideal_{cat}": 1.0 for cat in CATEGORIES},
    **{f"mult_{code}": 1.0 for code in INDICATOR_CODES},
}


@st.cache_data
def load_raw() -> pd.DataFrame:
    """Cached World Bank dataset (mock data until the first refresh)."""
    return load_dataset()


@st.cache_data
def load_matrix(max_missing: int) -> pd.DataFrame:
    """Normalized indicator matrix for the given missing-data tolerance."""
    return normalize(load_raw(), max_missing=max_missing)


@st.cache_data
def load_names(lang: str) -> pd.Series:
    """Country names in the given language, indexed by iso3."""
    return country_names(load_raw()["country"], lang)


def lang() -> str:
    """Language chosen in the sidebar."""
    return st.session_state.lang


def dark() -> bool:
    """Whether the viewer uses Streamlit's dark theme (charts pick matching colors)."""
    return st.context.theme.type == "dark"


def tr(key: str, **fmt: object) -> str:
    """Translate `key` into the current language."""
    return t(key, lang(), **fmt)


def relabel_countries() -> None:
    """on_change of the language: re-send country widgets' values so the browser shows the new names.

    The frontend otherwise keeps the old-language labels of already selected options.
    """
    for key in COUNTRY_WIDGETS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def init_state() -> None:
    """Seed defaults and keep values of widgets that are hidden in some modes."""
    for key, value in DEFAULTS.items():
        st.session_state[key] = st.session_state.get(key, value)


def apply_preset(preset_id: str) -> None:
    """on_click: load a preset's weights and ideal into the sidebar widgets."""
    preset = PRESETS[preset_id]
    for cat in CATEGORIES:
        st.session_state[cat] = preset["weights"].get(cat, 0)
        st.session_state[f"ideal_{cat}"] = preset.get("ideal", {}).get(cat, 1.0)
    for code in INDICATOR_CODES:
        st.session_state[f"mult_{code}"] = 1.0
    st.session_state.mode = MODE_IDEAL if preset.get("ideal") else MODE_BEST


def refresh_data() -> None:
    """on_click: download fresh data from the World Bank and drop cached frames."""
    try:
        load_dataset(refresh=True)
    except requests.RequestException:
        st.session_state.refresh_failed = True
        return
    st.session_state.refresh_failed = False
    st.cache_data.clear()


def sidebar(X: pd.DataFrame, names: pd.Series, regions: pd.Series) -> None:
    """Render all controls; their values are read back from st.session_state.

    format_func closures bind `lng` instead of reading session state, because
    Streamlit (and AppTest) may call them outside the script run.
    """
    sb, lng = st.sidebar, lang()
    sb.selectbox(tr("language"), list(LANGUAGES), format_func=LANGUAGES.get, key="lang",
                 on_change=relabel_countries)
    sb.radio(tr("mode"), [MODE_BEST, MODE_IDEAL, MODE_SIMILAR],
             format_func=lambda mode: t(f"mode.{mode}", lng), key="mode")
    mode = st.session_state.mode

    sb.subheader(tr("presets"))
    with sb.container(horizontal=True, wrap=True, gap="small"):
        for preset_id in PRESETS:
            st.button(label("preset", preset_id, lng), on_click=apply_preset, args=(preset_id,), width="content")

    sb.subheader(tr("weights"))
    if mode == MODE_SIMILAR:
        sb.caption(tr("uniform_note"))
    for cat in CATEGORIES:
        sb.slider(label("cat", cat, lng), 0, 10, key=cat, disabled=mode == MODE_SIMILAR)

    if mode == MODE_IDEAL:
        sb.subheader(tr("desired"))
        for cat in CATEGORIES:
            sb.slider(label("cat", cat, lng), 0.0, 1.0, step=0.05, key=f"ideal_{cat}")
    if mode == MODE_SIMILAR:
        options = sorted(X.index, key=names.get)
        st.session_state.setdefault("ref_country", options[0])
        sb.selectbox(tr("ref_country"), options, format_func=names.get, key="ref_country",
                     placeholder=tr("choose"))

    with sb.expander(tr("fine_tune")):
        st.caption(tr("fine_tune_note"))
        for code in INDICATOR_CODES:
            st.slider(label("ind", code, lng), 0.0, 2.0, step=0.1, key=f"mult_{code}",
                      disabled=mode == MODE_SIMILAR)

    sb.subheader(tr("filters"))
    sb.multiselect(tr("regions"), sorted(regions.dropna().unique()), key="regions",
                   format_func=lambda region: label("region", region, lng), placeholder=tr("all_regions"))
    sb.toggle(tr("complete_only"), key="complete_only")
    sb.button(tr("refresh"), on_click=refresh_data, width="stretch")
    if st.session_state.get("refresh_failed"):
        sb.error(tr("refresh_error"))


def run_query(X: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Score, per-indicator loss and the ideal profile for the current mode."""
    state = st.session_state
    if state.mode == MODE_SIMILAR:
        score, loss = similar_to(X, state.ref_country)
        return score, loss, X.loc[state.ref_country]
    mults = pd.Series({code: state[f"mult_{code}"] for code in INDICATOR_CODES})
    weights = expand_weights({cat: state[cat] for cat in CATEGORIES}) * mults
    if state.mode == MODE_IDEAL:
        ideal = pd.Series({ind.code: state[f"ideal_{ind.category}"] for ind in INDICATORS})
    else:
        ideal = pd.Series(1.0, index=X.columns)
    return *match(X, ideal, weights), ideal


def filter_regions(score: pd.Series, loss: pd.DataFrame,
                   regions: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    """Keep only countries from the regions chosen in the sidebar (all if none)."""
    chosen = st.session_state.regions
    if not chosen:
        return score, loss
    keep = regions[score.index].isin(chosen).to_numpy()
    return score[keep], loss[keep]


def top_cards(score: pd.Series, lost: pd.DataFrame, names: pd.Series) -> None:
    """Top-5 countries as bordered cards that wrap (two per row on phones)."""
    with st.container(horizontal=True, wrap=True, gap="small"):
        for rank, (iso3, value) in enumerate(score.head(5).items(), start=1):
            reasons = top_reasons(lost, iso3, lang=lang())
            st.metric(f"{rank}. {names[iso3]}", f"{value:.1f}", border=True, width=CARD_WIDTH,
                      help=tr("weakest", reasons=", ".join(reasons)) if reasons else None)


def ranking_tab(score: pd.Series, lost: pd.DataFrame, names: pd.Series, regions: pd.Series) -> None:
    """Full ranking table (score before region, so it stays visible on phones) plus the loss chart."""
    country, region, points = tr("col.country"), tr("col.region"), tr("col.score")
    table = pd.DataFrame({
        country: names[score.index].values,
        points: score.values,
        region: [label("region", r, lang()) for r in regions[score.index]],
    }, index=pd.RangeIndex(1, len(score) + 1, name="#"))
    st.dataframe(table, width="stretch", height=TABLE_HEIGHT, column_config={
        points: st.column_config.ProgressColumn(points, min_value=0, max_value=100, format="%.1f",
                                                width="medium"),
    })
    fig = loss_bar(loss_by_category(lost), names, lang(), dark=dark())
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


def compare_tab(X: pd.DataFrame, score: pd.Series, ideal: pd.Series, names: pd.Series) -> None:
    """Radar of up to three chosen countries against the ideal.

    The limit is enforced here rather than with max_selections, whose message is English-only.
    """
    chosen = st.multiselect(tr("compare_pick"), list(score.index), default=list(score.index[:MAX_COMPARE]),
                            format_func=names.get, key="compare", placeholder=tr("choose"))
    if len(chosen) > MAX_COMPARE:
        st.warning(tr("compare_limit"))
    if chosen:
        fig = radar(X.loc[chosen[:MAX_COMPARE]], ideal, names, lang(), dark=dark())
        st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


def why_not_block(score: pd.Series, lost: pd.DataFrame, names: pd.Series) -> None:
    """Explain what separates a chosen country from the winner, indicator by indicator."""
    winner = score.index[0]
    st.subheader(tr("why_not.title", winner=names[winner]), divider="gray")
    other = st.selectbox(tr("why_not.pick"), list(score.index[1:]), format_func=names.get,
                         key="why_not", placeholder=tr("choose"))
    st.markdown(tr("why_not.summary", other=names[other], other_score=f"{score[other]:.1f}",
                   winner=names[winner], winner_score=f"{score[winner]:.1f}"))
    table = why_not(lost, other, winner, lang=lang())
    gap = table[tr("col.gap")]
    st.plotly_chart(gap_bar(gap, names[other], names[winner], lang(), dark=dark()),
                    width="stretch", config=PLOTLY_CONFIG)
    with st.expander(tr("why_not.details")):
        fmt = st.column_config.NumberColumn(format="%.1f")
        st.dataframe(table, width="stretch", column_config=dict.fromkeys(table.columns, fmt))


def main() -> None:
    """Page entry point."""
    init_state()
    st.set_page_config(page_title=tr("page_title"), page_icon="🌍", layout="wide")
    raw = load_raw()
    names, regions = load_names(lang()), raw["region"]
    X = load_matrix(0 if st.session_state.get("complete_only") else 2)
    sidebar(X, names, regions)

    st.title(f"🌍 {tr('page_title')}")
    st.caption(tr("subtitle"))
    if not DATASET_PATH.exists():
        st.caption(tr("demo_data"))

    score, loss, ideal = run_query(X)
    score, loss = filter_regions(score, loss, regions)
    if score.empty:
        st.info(tr("no_results"))
        st.stop()
    lost = points_lost(loss)

    top_cards(score, lost, names)
    tab_rank, tab_compare, tab_map = st.tabs([tr("tab.rank"), tr("tab.compare"), tr("tab.map")])
    with tab_rank:
        ranking_tab(score, lost, names, regions)
    with tab_compare:
        compare_tab(X, score, ideal, names)
    with tab_map:
        st.plotly_chart(world_map(score, names, lang(), dark=dark()), width="stretch", config=PLOTLY_CONFIG)
    if len(score) > 1:
        why_not_block(score, lost, names)


main()
