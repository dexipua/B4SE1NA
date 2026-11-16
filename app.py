"""Streamlit UI for Country Matcher; all logic lives in the other modules."""

from pathlib import Path

import pandas as pd
import streamlit as st

from charts import loss_bar, radar, world_map
from config import CATEGORIES, INDICATORS, INDICATOR_CODES
from explain import top_reasons, why_not
from presets import PRESETS
from processing import normalize
from scoring import expand_weights, loss_by_category, match

DATA_DIR = Path(__file__).parent / "data"
DATASET, MOCK_DATASET = DATA_DIR / "dataset.csv", DATA_DIR / "mock_dataset.csv"
MODE_BEST, MODE_IDEAL, MODE_SIMILAR = "Найкраща", "Мій ідеал", "Схожі на країну"
DEFAULTS: dict[str, object] = {
    "mode": MODE_BEST,
    **{cat: 5 for cat in CATEGORIES},
    **{f"ideal_{cat}": 1.0 for cat in CATEGORIES},
    **{f"mult_{code}": 1.0 for code in INDICATOR_CODES},
}


@st.cache_data
def load_raw() -> tuple[pd.DataFrame, bool]:
    """Read the real dataset, falling back to mock data; also report which one."""
    is_mock = not DATASET.exists()
    return pd.read_csv(MOCK_DATASET if is_mock else DATASET, index_col="iso3"), is_mock


@st.cache_data
def load_matrix(max_missing: int) -> pd.DataFrame:
    """Normalized indicator matrix for the given missing-data tolerance."""
    return normalize(load_raw()[0], max_missing=max_missing)


def init_state() -> None:
    """Seed defaults and keep values of widgets that are hidden in some modes."""
    for key, value in DEFAULTS.items():
        st.session_state[key] = st.session_state.get(key, value)


def apply_preset(name: str) -> None:
    """on_click: load a preset's weights and ideal into the sidebar widgets."""
    preset = PRESETS[name]
    for cat in CATEGORIES:
        st.session_state[cat] = preset["weights"].get(cat, 0)
        st.session_state[f"ideal_{cat}"] = preset.get("ideal", {}).get(cat, 1.0)
    for code in INDICATOR_CODES:
        st.session_state[f"mult_{code}"] = 1.0
    st.session_state.mode = MODE_IDEAL if preset.get("ideal") else MODE_BEST


def sidebar(X: pd.DataFrame, names: pd.Series, regions: pd.Series) -> None:
    """Render all controls; their values are read back from st.session_state."""
    sb = st.sidebar
    sb.radio("Режим", [MODE_BEST, MODE_IDEAL, MODE_SIMILAR], key="mode")
    mode = st.session_state.mode

    sb.subheader("Готові профілі")
    for col, name in zip(sb.columns(len(PRESETS)), PRESETS):
        col.button(name, on_click=apply_preset, args=(name,), width="stretch")

    sb.subheader("Важливість категорій")
    if mode == MODE_SIMILAR:
        sb.caption("У цьому режимі всі показники мають рівну вагу.")
    for cat, label in CATEGORIES.items():
        sb.slider(label, 0, 10, key=cat, disabled=mode == MODE_SIMILAR)

    if mode == MODE_IDEAL:
        sb.subheader("Бажаний рівень")
        for cat, label in CATEGORIES.items():
            sb.slider(label, 0.0, 1.0, step=0.05, key=f"ideal_{cat}")
    if mode == MODE_SIMILAR:
        options = sorted(X.index, key=names.get)
        st.session_state.setdefault("ref_country", options[0])
        sb.selectbox("Країна-зразок", options, format_func=names.get, key="ref_country")

    with sb.expander("Тонке налаштування показників"):
        st.caption("Множник ваги показника всередині його категорії.")
        for ind in INDICATORS:
            st.slider(ind.label, 0.0, 2.0, step=0.1, key=f"mult_{ind.code}",
                      disabled=mode == MODE_SIMILAR)

    sb.multiselect("Регіони", sorted(regions.dropna().unique()), key="regions",
                   placeholder="Усі регіони")
    sb.toggle("Лише країни з повними даними", key="complete_only")


def build_query(X: pd.DataFrame) -> tuple[pd.Series, pd.Series, list[str]]:
    """Ideal vector, indicator weights and countries to exclude for the current mode."""
    state = st.session_state
    if state.mode == MODE_SIMILAR:
        ref = state.ref_country
        return X.loc[ref], pd.Series(1.0, index=X.columns), [ref]
    mults = pd.Series({code: state[f"mult_{code}"] for code in INDICATOR_CODES})
    weights = expand_weights({cat: state[cat] for cat in CATEGORIES}) * mults
    if state.mode == MODE_IDEAL:
        ideal = pd.Series({ind.code: state[f"ideal_{ind.category}"] for ind in INDICATORS})
    else:
        ideal = pd.Series(1.0, index=X.columns)
    return ideal, weights, []


def top_cards(score: pd.Series, loss: pd.DataFrame, names: pd.Series) -> None:
    """Top-5 countries as metric cards; tooltip lists their weakest indicators."""
    top = score.head(5)
    for rank, (col, (iso3, value)) in enumerate(zip(st.columns(len(top)), top.items()), start=1):
        reasons = top_reasons(loss, iso3)
        col.metric(f"{rank}. {names[iso3]}", f"{value:.1f}",
                   help="Найбільше відстає: " + ", ".join(reasons) if reasons else None)


def ranking_tab(score: pd.Series, loss: pd.DataFrame, names: pd.Series, regions: pd.Series) -> None:
    """Full ranking table plus the per-category loss chart."""
    table = pd.DataFrame({
        "Країна": names[score.index].values,
        "Регіон": regions[score.index].values,
        "Бал": score.values,
    }, index=pd.RangeIndex(1, len(score) + 1, name="#"))
    st.dataframe(table, width="stretch", column_config={
        "Бал": st.column_config.ProgressColumn("Бал", min_value=0, max_value=100, format="%.1f"),
    })
    st.plotly_chart(loss_bar(loss_by_category(loss), names), width="stretch")


def compare_tab(X: pd.DataFrame, score: pd.Series, ideal: pd.Series, names: pd.Series) -> None:
    """Radar of up to three chosen countries against the ideal."""
    chosen = st.multiselect("Країни для порівняння (до 3)", list(score.index),
                            default=list(score.index[:3]), max_selections=3,
                            format_func=names.get, key="compare")
    if chosen:
        st.plotly_chart(radar(X.loc[chosen], ideal, names), width="stretch")


def why_not_block(score: pd.Series, loss: pd.DataFrame, names: pd.Series) -> None:
    """Explain what separates a chosen country from the winner."""
    winner = score.index[0]
    st.subheader(f"Чому не X, а {names[winner]}?")
    other = st.selectbox("Країна X", list(score.index[1:]), format_func=names.get, key="why_not")
    st.write(f"**{names[other]}**: {score[other]:.1f} балів проти {score[winner]:.1f} "
             f"у **{names[winner]}**. Де втрачено найбільше (внесок у відстань до ідеалу):")
    fmt = st.column_config.NumberColumn(format="%.4f")
    st.dataframe(why_not(loss, other, winner), width="stretch",
                 column_config={"Країна": fmt, "Лідер": fmt, "Різниця": fmt})


def main() -> None:
    """Page entry point."""
    st.set_page_config(page_title="Підбір країни", page_icon="🌍", layout="wide")
    init_state()
    raw, is_mock = load_raw()
    names, regions = raw["country"], raw["region"]
    X = load_matrix(0 if st.session_state.get("complete_only") else 2)
    sidebar(X, names, regions)

    st.title("🌍 Підбір країни за вашим профілем")
    if is_mock:
        st.caption("Демо-дані: data/dataset.csv ще не створено, використано mock_dataset.csv.")

    ideal, weights, exclude = build_query(X)
    pool = X[regions[X.index].isin(st.session_state.regions)] if st.session_state.regions else X
    score, loss = match(pool.drop(index=exclude, errors="ignore"), ideal, weights)
    if score.empty:
        st.info("Немає результатів: задайте ненульову вагу хоча б одній категорії "
                "або розширте фільтр регіонів.")
        st.stop()

    top_cards(score, loss, names)
    tab_rank, tab_compare, tab_map = st.tabs(["Рейтинг", "Порівняння", "Карта"])
    with tab_rank:
        ranking_tab(score, loss, names, regions)
    with tab_compare:
        compare_tab(X, score, ideal, names)
    with tab_map:
        st.plotly_chart(world_map(score, names), width="stretch")
    if len(score) > 1:
        why_not_block(score, loss, names)


main()
