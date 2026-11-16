"""Plotly figures for the app; no Streamlit here. All text is translated via i18n.

Every figure shares one style (palette, fonts, tooltips, margins) that adapts to light/dark
mode, and keeps legends horizontal so charts don't lose width on narrow screens.
"""

import re
import textwrap
from typing import NamedTuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import CATEGORIES, INDICATOR_CODES
from i18n import label, t


class Palette(NamedTuple):
    """Colors for one theme; categorical order is fixed so a category keeps its color."""

    series: list[str]
    muted: str
    surface: str
    text: str
    grid: str
    land: str
    sequential: list[str]


LIGHT = Palette(
    series=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"],
    muted="#8a8984", surface="#ffffff", text="#31333f", grid="#e6e6e3", land="#ececea",
    sequential=["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"],
)
DARK = Palette(
    series=["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c"],
    muted="#9b9a95", surface="#0e1117", text="#fafafa", grid="#33353d", land="#262730",
    sequential=["#0d366b", "#1c5cab", "#3987e5", "#86b6ef", "#cde2fb"],
)
FONT_SIZE = 13
LABEL_WRAP = 16  # characters per line for long labels (CJK characters count double)
RADAR_WRAP = 13
CJK = re.compile(r"[　-鿿＀-￯]")  # CJK punctuation, ideographs, full-width forms
CJK_TOKEN = re.compile(r"[A-Za-z0-9.,%$]+|\s+|.")  # Latin/number runs are unbreakable
CJK_NO_LINE_START = set("，。、）：；%")


def palette(dark: bool) -> Palette:
    """Palette for the active theme."""
    return DARK if dark else LIGHT


def hyphenate(word: str, width: int) -> list[str]:
    """Split a word that is much longer than `width` into hyphenated pieces."""
    if len(word) <= width + 3:  # a slightly long word reads better whole
        return [word]
    return [word[:width - 1] + "-", *hyphenate(word[width - 1:], width)]


def wrap_cjk(text: str, width: int) -> list[str]:
    """Greedy CJK line breaking by display width (ideographs count 2).

    Latin/number runs such as "GDP" or "PM2.5" stay whole, and closing punctuation
    never starts a line.
    """
    lines = [""]
    for token in CJK_TOKEN.findall(text):
        line_width = sum(2 if CJK.match(ch) else 1 for ch in lines[-1])
        token_width = sum(2 if CJK.match(ch) else 1 for ch in token)
        if lines[-1] and line_width + token_width > width and token not in CJK_NO_LINE_START:
            lines.append("")
        lines[-1] += token
    return lines


def wrap(text: str, width: int = LABEL_WRAP) -> str:
    """Break a long label into lines so it is not clipped on narrow screens.

    Words stay whole unless they would overflow badly, in which case they are hyphenated.
    """
    if CJK.search(text):
        return "<br>".join(wrap_cjk(text, width))
    words = " ".join(part for word in text.split() for part in hyphenate(word, width))
    return "<br>".join(textwrap.wrap(words, width, break_long_words=False, break_on_hyphens=False)) or text


def styled(fig: go.Figure, pal: Palette, height: int) -> go.Figure:
    """Apply the shared look: transparent background, readable tooltips, compact margins."""
    fig.update_layout(
        height=height,
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"size": FONT_SIZE, "color": pal.text},
        hoverlabel={"bgcolor": pal.surface, "bordercolor": pal.grid,
                    "font": {"size": FONT_SIZE, "color": pal.text}, "align": "left"},
        legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.0, "yanchor": "bottom",
                "title_text": "", "font": {"size": FONT_SIZE - 1}},
    )
    return fig


def loss_bar(lost_cat: pd.DataFrame, names: pd.Series, lang: str, top_n: int = 10,
             dark: bool = False) -> go.Figure:
    """Stacked bars: how many score points each category costs the top countries."""
    pal = palette(dark)
    data = lost_cat.head(top_n).rename(index=names, columns={c: label("cat", c, lang) for c in CATEGORIES})
    fig = px.bar(data, orientation="h", color_discrete_sequence=pal.series)
    fig.update_traces(marker_line={"width": 1.5, "color": pal.surface},
                      hovertemplate="%{x:.1f}<extra>%{fullData.name}</extra>")
    fig.update_layout(
        hovermode="y unified", bargap=0.3,
        xaxis={"title": t("chart.points_lost", lang), "gridcolor": pal.grid, "zeroline": False,
               "rangemode": "tozero"},
        yaxis={"title": "", "autorange": "reversed", "automargin": True},
    )
    return styled(fig, pal, height=90 + 34 * len(data))


def radar(rows: pd.DataFrame, ideal: pd.Series, names: pd.Series, lang: str,
          dark: bool = False) -> go.Figure:
    """Radar over all indicators (0-100 relative level): selected countries vs the ideal."""
    pal = palette(dark)
    theta = [wrap(label("ind", code, lang), RADAR_WRAP) for code in INDICATOR_CODES]
    traces = [(names[iso3], rows.loc[iso3], color, "solid") for iso3, color in zip(rows.index, pal.series)]
    traces.append((t("chart.ideal", lang), ideal, pal.muted, "dash"))
    fig = go.Figure()
    for name, values, color, dash in traces:
        r = (values[INDICATOR_CODES] * 100).tolist()
        fig.add_trace(go.Scatterpolar(
            r=r + r[:1], theta=theta + theta[:1], name=name, mode="lines+markers",
            line={"color": color, "width": 2, "dash": dash}, marker={"size": 6},
            hovertemplate="<b>" + name + "</b><br>%{theta}: %{r:.0f}<extra></extra>",
        ))
    fig.update_layout(polar={
        "bgcolor": "rgba(0,0,0,0)",
        # Side room for labels on phones; on desktop the circle is height-bound, so this costs nothing.
        "domain": {"x": [0.2, 0.8], "y": [0.0, 0.9]},
        # Ticks sit between the first two spokes (at 90 and 54 degrees) so they never cover a label.
        "radialaxis": {"range": [0, 105], "tickvals": [25, 50, 75, 100], "angle": 72, "tickangle": 72,
                       "tickfont": {"size": FONT_SIZE - 3, "color": pal.muted}, "gridcolor": pal.grid,
                       "showline": False},
        "angularaxis": {"rotation": 90, "direction": "clockwise", "gridcolor": pal.grid,
                        "linecolor": pal.grid, "tickfont": {"size": FONT_SIZE - 2}},
    })
    return styled(fig, pal, height=500).update_layout(margin={"b": 56})


def world_map(score: pd.Series, names: pd.Series, lang: str, dark: bool = False) -> go.Figure:
    """Choropleth of match scores; countries without a score stay neutral grey."""
    pal = palette(dark)
    score_col = t("col.score", lang)
    data = pd.DataFrame({"iso3": score.index, "name": names[score.index].values, score_col: score.values})
    fig = px.choropleth(data, locations="iso3", color=score_col, hover_name="name",
                        custom_data=[score_col], color_continuous_scale=pal.sequential)
    fig.update_traces(marker_line={"width": 0.4, "color": pal.surface},
                      hovertemplate="<b>%{hovertext}</b><br>" + score_col + ": %{customdata[0]:.1f}<extra></extra>")
    fig.update_geos(
        projection_type="natural earth", lataxis_range=[-57, 84], showframe=False,
        showcoastlines=False, showland=True, landcolor=pal.land, showocean=False,
        showcountries=True, countrycolor=pal.surface, bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(coloraxis_colorbar={
        "orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.02, "yanchor": "top",
        "len": 0.5, "thickness": 10, "title": {"text": score_col, "side": "top"},
    })
    return styled(fig, pal, height=460)


def gap_bar(gap: pd.Series, other: str, winner: str, lang: str, dark: bool = False) -> go.Figure:
    """Diverging bars: per-indicator difference in points lost (positive = `other` loses more)."""
    pal = palette(dark)
    gap = gap[gap.abs() >= 0.05].sort_values()
    worse, better = pal.series[1], pal.series[0]
    fig = go.Figure(go.Bar(
        x=gap.values, y=[wrap(i, 28) for i in gap.index], orientation="h",
        marker={"color": [worse if v > 0 else better for v in gap.values]},
        hovertemplate="<b>%{y}</b><br>%{x:+.1f}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=False, bargap=0.35,
        xaxis={"title": wrap(t("chart.gap_axis", lang, other=other, winner=winner), 22), "gridcolor": pal.grid,
               "zeroline": True, "zerolinecolor": pal.muted, "zerolinewidth": 1},
        yaxis={"automargin": True},
    )
    return styled(fig, pal, height=90 + 34 * max(len(gap), 1))


def score_bar(score: pd.Series, names: pd.Series, lang: str, top_n: int = 10,
              dark: bool = False) -> go.Figure:
    """Horizontal bars of the top countries' scores, best on top, value at the bar's end."""
    pal = palette(dark)
    top = score.nlargest(top_n)
    score_col = t("col.score", lang)
    fig = go.Figure(go.Bar(
        x=top.values, y=names[top.index].values, orientation="h", marker={"color": pal.series[0]},
        texttemplate="%{x:.1f}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>" + score_col + ": %{x:.1f}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=False, bargap=0.3,
        xaxis={"title": score_col, "range": [0, 100], "gridcolor": pal.grid, "zeroline": False},
        yaxis={"autorange": "reversed", "automargin": True},
    )
    return styled(fig, pal, height=90 + 34 * len(top))


def category_scatter(levels: pd.DataFrame, score: pd.Series, names: pd.Series, lang: str,
                     x_cat: str = "safety", y_cat: str = "economy", dark: bool = False) -> go.Figure:
    """Countries placed by two category levels (0-100, default safety vs economy), colored by score."""
    pal = palette(dark)
    data = levels.loc[score.index, [x_cat, y_cat]].dropna()
    score_col, x_label, y_label = t("col.score", lang), label("cat", x_cat, lang), label("cat", y_cat, lang)
    fig = go.Figure(go.Scatter(
        x=data[x_cat], y=data[y_cat], mode="markers", text=names[data.index], customdata=score[data.index],
        marker={"size": 10, "color": score[data.index], "colorscale": pal.sequential,
                "line": {"width": 0.5, "color": pal.surface},
                "colorbar": {"title": {"text": score_col}, "thickness": 10}},
        hovertemplate=(f"<b>%{{text}}</b><br>{x_label}: %{{x:.0f}}<br>{y_label}: %{{y:.0f}}"
                       f"<br>{score_col}: %{{customdata:.1f}}<extra></extra>"),
    ))
    axis = {"range": [-5, 105], "gridcolor": pal.grid, "zeroline": False}
    fig.update_layout(xaxis={**axis, "title": x_label}, yaxis={**axis, "title": y_label})
    return styled(fig, pal, height=480)


def why_not_bar(lost_cat: pd.DataFrame, names: pd.Series, iso3: str, winner: str, lang: str,
                dark: bool = False) -> go.Figure:
    """'Why not X?' by category: points X loses minus points the winner loses (positive = X is worse)."""
    gap = (lost_cat.loc[iso3] - lost_cat.loc[winner]).rename(index=lambda cat: label("cat", cat, lang))
    return gap_bar(gap, names[iso3], names[winner], lang, dark=dark)


def category_profile(levels: pd.Series, lang: str, dark: bool = False) -> go.Figure:
    """One country's level (0-100, relative to all countries) in each category, one colored bar each."""
    pal = palette(dark)
    names = [label("cat", cat, lang) for cat in levels.index]
    fig = go.Figure(go.Bar(
        x=levels.values, y=names, orientation="h", marker={"color": pal.series[:len(levels)]},
        texttemplate="%{x:.0f}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b>: %{x:.0f}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=False, bargap=0.3,
        xaxis={"title": t("profile.levels", lang), "range": [0, 100], "gridcolor": pal.grid, "zeroline": False},
        yaxis={"autorange": "reversed", "automargin": True},
    )
    return styled(fig, pal, height=90 + 34 * len(levels))
