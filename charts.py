"""Plotly figures for the app; no Streamlit here."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import CATEGORIES, INDICATOR_CODES, LABEL_OF

SERIES_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
IDEAL_COLOR = "#8a8984"
SEQUENTIAL = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]


def loss_bar(loss_cat: pd.DataFrame, names: pd.Series, top_n: int = 10) -> go.Figure:
    """Stacked bars: how much each category pulls the top countries from the ideal."""
    data = loss_cat.head(top_n).rename(index=names, columns=CATEGORIES)
    fig = px.bar(
        data,
        orientation="h",
        color_discrete_sequence=SERIES_COLORS,
        labels={"value": "Внесок у відстань до ідеалу", "index": "", "variable": "Категорія"},
    )
    fig.update_layout(yaxis={"autorange": "reversed"}, bargap=0.35, legend_title_text="")
    fig.update_traces(marker_line_width=0, hovertemplate="%{y}: %{x:.4f}<extra>%{fullData.name}</extra>")
    return fig


def radar(rows: pd.DataFrame, ideal: pd.Series, names: pd.Series) -> go.Figure:
    """Radar over all indicators: selected countries vs the ideal profile."""
    labels = [LABEL_OF[code] for code in INDICATOR_CODES]
    fig = go.Figure()
    traces = [(names[iso3], rows.loc[iso3], color, "solid") for iso3, color in zip(rows.index, SERIES_COLORS)]
    traces.append(("Ідеал", ideal, IDEAL_COLOR, "dash"))
    for name, values, color, dash in traces:
        r = values[INDICATOR_CODES].tolist()
        fig.add_trace(go.Scatterpolar(
            r=r + r[:1], theta=labels + labels[:1], name=name,
            line={"color": color, "width": 2, "dash": dash},
            hovertemplate="%{theta}: %{r:.2f}<extra>" + name + "</extra>",
        ))
    fig.update_layout(polar={"radialaxis": {"range": [0, 1]}}, legend={"orientation": "h"})
    return fig


def world_map(score: pd.Series, names: pd.Series) -> go.Figure:
    """Choropleth of match scores."""
    data = pd.DataFrame({"iso3": score.index, "Країна": names[score.index].values, "Бал": score.values})
    fig = px.choropleth(
        data, locations="iso3", color="Бал", hover_name="Країна",
        hover_data={"iso3": False, "Бал": ":.1f"}, color_continuous_scale=SEQUENTIAL,
    )
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0}, geo={"showframe": False})
    return fig

def score_bar(score: pd.Series, names: pd.Series, top_n: int = 10) -> go.Figure:
    """Horizontal bars of match scores for the top countries (higher is better)."""
    top = score.dropna().sort_values(ascending=False).head(top_n)
    if top.empty:
        return go.Figure()
    data = pd.DataFrame({"Країна": names[top.index].values, "Бал": top.values})
    fig = px.bar(
        data, x="Бал", y="Країна", orientation="h", text="Бал",
        color_discrete_sequence=[SERIES_COLORS[0]],
    )
    fig.update_traces(
        marker_line_width=0, texttemplate="%{text:.1f}", textposition="outside",
        hovertemplate="%{y}: %{x:.1f}<extra></extra>",
    )
    fig.update_layout(yaxis={"autorange": "reversed", "title": ""}, bargap=0.35)
    return fig

def category_scatter(
        cat: pd.DataFrame,
        score: pd.Series,
        names: pd.Series,
        x_cat: str = "safety",
        y_cat: str = "economy",
) -> go.Figure:
    """Scatter of countries by two categories (default: safety vs economy), colored by score."""
    data = pd.DataFrame({
        "iso3": cat.index,
        "Країна": names[cat.index].values,
        "x": cat[x_cat].values,
        "y": cat[y_cat].values,
        "Бал": score.reindex(cat.index).values,
    }).dropna(subset=["x", "y"])
    if data.empty:
        return go.Figure()
    fig = px.scatter(
        data, x="x", y="y", color="Бал", hover_name="Країна",
        hover_data={"iso3": False, "x": ":.2f", "y": ":.2f", "Бал": ":.1f"},
        color_continuous_scale=SEQUENTIAL,
        labels={"x": CATEGORIES[x_cat], "y": CATEGORIES[y_cat]},
    )
    fig.update_traces(marker={"size": 9, "line": {"width": 0}})
    return fig
