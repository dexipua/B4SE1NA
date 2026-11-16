"""Streamlit UI for Country Matcher; all logic lives in the other modules."""

from urllib.parse import urlencode, urlsplit

import pandas as pd
import requests
import streamlit as st

from charts import category_scatter, gap_bar, loss_bar, radar, score_bar, why_not_bar, world_map
from config import CATEGORIES, INDICATOR_CODES
from data_loader import DATASET_PATH, load_dataset
from explain import ranking_table, top_reasons, values_table, why_not
from i18n import LANGUAGES, country_names, label, t
from presets import PRESETS
from processing import normalize
from quiz import QUESTIONS, quiz_settings, top_categories
from scoring import category_levels, loss_by_category, match, points_lost, similar_to
from settings import DEFAULTS, MODE_BEST, MODE_IDEAL, MODE_SIMILAR, decode, encode, preset_settings, query

MAX_COMPARE = 3
CSV_NAME = "country-ranking.csv"
CARD_WIDTH = "stretch"  # cards share the row and wrap on narrow screens
COUNTRY_WIDGETS = ("ref_country", "compare", "why_not", "regions")
TABLE_HEIGHT = 386  # px: ten rows plus the header, no half-visible row
PLOTLY_CONFIG = {"displayModeBar": False}  # plotly's modebar tooltips are English-only
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


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


def local_visit() -> bool:
    """Whether the page is opened on this machine rather than through a public tunnel (ngrok).

    ngrok routes by the Host header, so a remote visitor cannot pose as localhost.
    No Host header means a headless test run, which counts as local.
    """
    host = st.context.headers.get("Host")
    return host is None or urlsplit(f"//{host}").hostname in LOCAL_HOSTS


def show(fig: object) -> None:
    """Render a plotly figure full-width without plotly's English-only toolbar."""
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


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


def init_state(raw: pd.DataFrame) -> None:
    """Apply a shared link once per session, then seed defaults and keep hidden widgets' values."""
    state = st.session_state
    if "link_applied" not in state:
        state.update(decode(st.query_params.to_dict(), raw.index, set(raw["region"].dropna())))
        state.link_applied = True
    for key, value in DEFAULTS.items():
        state[key] = state.get(key, value)


def apply_preset(preset_id: str) -> None:
    """on_click: load a preset's weights and ideal into the sidebar widgets."""
    st.session_state.update(preset_settings(preset_id))


def apply_quiz() -> None:
    """on_click: turn the quiz answers into weights, multipliers and ideal, like a personal preset."""
    settings = quiz_settings({q: st.session_state[f"quiz_{q}"] for q in QUESTIONS})
    st.session_state.update(settings)
    st.session_state.quiz_top = top_categories(settings)


def quiz_body() -> None:
    """Quiz questions as radios with no default; applying needs every question answered."""
    lng = lang()
    st.caption(tr("quiz.intro", n=len(QUESTIONS)))
    for question, options in QUESTIONS.items():
        st.radio(t(f"quiz.{question}", lng), list(options), index=None, key=f"quiz_{question}",
                 format_func=lambda option, q=question: t(f"quiz.{q}.{option}", lng))
    answered = all(st.session_state.get(f"quiz_{q}") for q in QUESTIONS)
    st.button(tr("quiz.apply"), on_click=apply_quiz, disabled=not answered, type="primary", width="stretch")


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
    if sb.button(tr("quiz.open"), icon=":material/quiz:", width="stretch"):
        st.dialog(tr("quiz.title"), width="large")(quiz_body)()

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
    if local_visit():  # public visitors must not trigger World Bank downloads on the host
        sb.button(tr("refresh"), on_click=refresh_data, width="stretch")
    if st.session_state.get("refresh_failed"):
        sb.error(tr("refresh_error"))


def sync_link() -> None:
    """Mirror the settings into the address bar and offer a copyable link in the sidebar."""
    params = encode(st.session_state)
    st.query_params.from_dict(params)
    if st.context.url:
        st.sidebar.subheader(tr("share"))
        st.sidebar.code(f"{st.context.url}?{urlencode(params)}", language=None, wrap_lines=True)
        st.sidebar.caption(tr("share.note"))


def run_query(X: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Score, per-indicator loss and the ideal profile for the current mode."""
    state = st.session_state
    if state.mode == MODE_SIMILAR:
        score, loss = similar_to(X, state.ref_country)
        return score, loss, X.loc[state.ref_country]
    ideal, weights = query(state)
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


def ranking_tab(score: pd.Series, lost_cat: pd.DataFrame, names: pd.Series, regions: pd.Series) -> None:
    """Top-10 score bars, full ranking table (score before region, visible on phones), CSV, loss chart."""
    show(score_bar(score, names, lang(), dark=dark()))
    table = ranking_table(score, names, regions, lang())
    points = tr("col.score")
    st.dataframe(table.drop(columns="ISO3"), width="stretch", height=TABLE_HEIGHT, column_config={
        points: st.column_config.ProgressColumn(points, min_value=0, max_value=100, format="%.1f",
                                                width="medium"),
    })
    st.download_button(tr("download"), table.to_csv().encode("utf-8-sig"), file_name=CSV_NAME,
                       mime="text/csv", icon=":material/download:", on_click="ignore")
    show(loss_bar(lost_cat, names, lang(), dark=dark()))


def compare_tab(raw: pd.DataFrame, X: pd.DataFrame, score: pd.Series, ideal: pd.Series,
                names: pd.Series) -> None:
    """Radar of up to three chosen countries against the ideal, then their actual values.

    The limit is enforced here rather than with max_selections, whose message is English-only.
    """
    chosen = st.multiselect(tr("compare_pick"), list(score.index), default=list(score.index[:MAX_COMPARE]),
                            format_func=names.get, key="compare", placeholder=tr("choose"))
    if len(chosen) > MAX_COMPARE:
        st.warning(tr("compare_limit"))
    if not chosen:
        return
    shown = chosen[:MAX_COMPARE]
    show(radar(X.loc[shown], ideal, names, lang(), dark=dark()))
    st.subheader(tr("values.title"), divider="gray")
    st.dataframe(values_table(raw, shown, names, lang()), width="stretch")
    st.caption(tr("values.note"))


def explore_tab(X: pd.DataFrame, score: pd.Series, names: pd.Series) -> None:
    """Scatter of countries by two chosen categories (safety vs economy by default), colored by score."""
    lng = lang()
    x_col, y_col = st.columns(2)
    x_cat = x_col.selectbox(tr("explore.x"), CATEGORIES, index=CATEGORIES.index("safety"), key="explore_x",
                            format_func=lambda cat: label("cat", cat, lng))
    y_cat = y_col.selectbox(tr("explore.y"), CATEGORIES, index=CATEGORIES.index("economy"), key="explore_y",
                            format_func=lambda cat: label("cat", cat, lng))
    show(category_scatter(category_levels(X), score, names, lng, x_cat, y_cat, dark=dark()))
    st.caption(tr("explore.note"))


def why_not_block(score: pd.Series, lost: pd.DataFrame, lost_cat: pd.DataFrame, names: pd.Series) -> None:
    """Explain what separates a chosen country from the winner: by category, then by indicator."""
    winner = score.index[0]
    st.subheader(tr("why_not.title", winner=names[winner]), divider="gray")
    other = st.selectbox(tr("why_not.pick"), list(score.index[1:]), format_func=names.get,
                         key="why_not", placeholder=tr("choose"))
    st.markdown(tr("why_not.summary", other=names[other], other_score=f"{score[other]:.1f}",
                   winner=names[winner], winner_score=f"{score[winner]:.1f}"))
    show(why_not_bar(lost_cat, names, other, winner, lang(), dark=dark()))
    with st.expander(tr("why_not.details")):
        table = why_not(lost, other, winner, lang=lang())
        show(gap_bar(table[tr("col.gap")], names[other], names[winner], lang(), dark=dark()))
        fmt = st.column_config.NumberColumn(format="%.1f")
        st.dataframe(table, width="stretch", column_config=dict.fromkeys(table.columns, fmt))


def main() -> None:
    """Page entry point."""
    raw = load_raw()
    init_state(raw)
    st.set_page_config(page_title=tr("page_title"), page_icon="🌍", layout="wide")
    names, regions = load_names(lang()), raw["region"]
    X = load_matrix(0 if st.session_state.get("complete_only") else 2)
    sidebar(X, names, regions)
    sync_link()

    st.title(f"🌍 {tr('page_title')}")
    st.caption(tr("subtitle"))
    if quiz_top := st.session_state.pop("quiz_top", None):
        st.success(tr("quiz.done", cats=", ".join(label("cat", cat, lang()) for cat in quiz_top)))
    if not DATASET_PATH.exists():
        st.caption(tr("demo_data"))

    score, loss, ideal = run_query(X)
    score, loss = filter_regions(score, loss, regions)
    if score.empty:
        st.info(tr("no_results"))
        st.stop()
    lost = points_lost(loss)
    lost_cat = loss_by_category(lost)

    top_cards(score, lost, names)
    tab_rank, tab_compare, tab_explore, tab_map = st.tabs(
        [tr("tab.rank"), tr("tab.compare"), tr("tab.explore"), tr("tab.map")])
    with tab_rank:
        ranking_tab(score, lost_cat, names, regions)
    with tab_compare:
        compare_tab(raw, X, score, ideal, names)
    with tab_explore:
        explore_tab(X, score, names)
    with tab_map:
        show(world_map(score, names, lang(), dark=dark()))
    if len(score) > 1:
        why_not_block(score, lost, lost_cat, names)


main()
