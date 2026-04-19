"""
Incidental Coverage — Time-series analysis page.

Shows the percentage of high-suitability anchovy habitat that falls
inside any existing conservation closure, from 1997 to present.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.constants import THEMES, KEY_EVENTS, YEAR_MIN, YEAR_MAX
from utils.model_data import generate_coverage_timeseries

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
theme = THEMES[st.session_state.theme]


def inject_page_css(t):
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t["bg"]}; color: {t["text"]}; }}
        section[data-testid="stSidebar"] {{ background-color: {t["bg_secondary"]}; }}
        .stApp header, .stApp [data-testid="stHeader"] {{ display: none !important; }}

        /* Force text color everywhere */
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp li, .stApp td, .stApp th, .stApp strong, .stApp em, .stApp a,
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] span,
        .stApp [data-testid="stMarkdownContainer"] li,
        .stApp [data-testid="stMarkdownContainer"] h1,
        .stApp [data-testid="stMarkdownContainer"] h2,
        .stApp [data-testid="stMarkdownContainer"] h3,
        .stApp [data-testid="stMarkdownContainer"] strong,
        .stApp [data-testid="stCaptionContainer"] p,
        .stApp [data-testid="stWidgetLabel"] p,
        .stApp .stRadio label, .stApp .stCheckbox label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] strong,
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        .stApp details, .stApp details summary, .stApp details summary span,
        .stApp details > div, .stApp details p, .stApp details li,
        .stApp details span, .stApp details blockquote, .stApp details blockquote p,
        .stApp details strong, .stApp details em,
        .stApp [data-testid="stExpander"] p,
        .stApp [data-testid="stExpander"] li,
        .stApp [data-testid="stExpander"] span,
        .stApp [data-testid="stExpander"] strong {{
            color: {t["text"]} !important;
        }}

        .metric-card {{
            background: {t["card_bg"]};
            border: 1px solid {t["card_border"]};
            border-radius: 12px;
            padding: 24px 28px;
            text-align: center;
        }}
        .metric-card .metric-value {{
            font-size: 2.8rem; font-weight: 700;
            color: {t["accent"]} !important; line-height: 1.1;
        }}
        .metric-card .metric-label {{
            font-size: 0.9rem; color: {t["text"]} !important;
            opacity: 0.7; margin-top: 6px;
        }}
        .hero-title {{
            font-size: 2rem; font-weight: 800;
            color: {t["accent"]} !important;
            margin-bottom: 0; padding: 0;
        }}
        .hero-subtitle {{
            font-size: 1.05rem; opacity: 0.7;
            margin-top: 4px; color: {t["text"]} !important;
        }}
        .block-container {{ padding-top: 2rem; }}
    </style>
    """, unsafe_allow_html=True)


inject_page_css(theme)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📊 Incidental Coverage")
    st.divider()
    show_events = st.checkbox("Annotate key events", value=True)
    show_trend = st.checkbox("Show trend line", value=True)
    st.divider()
    st.caption("Data: Mock (pipeline pending)")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown('<p class="hero-title">Incidental Coverage Over Time</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">% of high-suitability anchovy habitat inside any existing closure</p>',
    unsafe_allow_html=True,
)

# Generate data
ts = generate_coverage_timeseries()
latest = ts[ts["year"] == YEAR_MAX]["coverage_pct"].values[0]
avg = ts["coverage_pct"].mean()
min_row = ts.loc[ts["coverage_pct"].idxmin()]
max_row = ts.loc[ts["coverage_pct"].idxmax()]

# ---------------------------------------------------------------------------
# Headline metrics
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{latest:.1f}%</div>
        <div class="metric-label">Current ({YEAR_MAX})</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg:.1f}%</div>
        <div class="metric-label">Average ({YEAR_MIN}–{YEAR_MAX})</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{min_row['coverage_pct']:.1f}%</div>
        <div class="metric-label">Minimum ({int(min_row['year'])})</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{max_row['coverage_pct']:.1f}%</div>
        <div class="metric-label">Maximum ({int(max_row['year'])})</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ---------------------------------------------------------------------------
# Plotly chart
# ---------------------------------------------------------------------------
fig = go.Figure()

# Area fill
fig.add_trace(go.Scatter(
    x=ts["year"],
    y=ts["coverage_pct"],
    fill="tozeroy",
    fillcolor="rgba(14, 165, 233, 0.15)",
    line=dict(color=theme["accent"], width=2.5),
    mode="lines",
    name="Incidental Coverage",
    hovertemplate="<b>%{x}</b><br>Coverage: %{y:.1f}%<extra></extra>",
))

# Trend line
if show_trend:
    import numpy as np
    z = np.polyfit(ts["year"], ts["coverage_pct"], 1)
    trend = np.polyval(z, ts["year"])
    fig.add_trace(go.Scatter(
        x=ts["year"],
        y=trend,
        line=dict(color="#94a3b8", width=1.5, dash="dash"),
        mode="lines",
        name="Linear Trend",
        hoverinfo="skip",
    ))

# Event annotations
if show_events:
    for event in KEY_EVENTS:
        yr = event["year"]
        cov = ts[ts["year"] == yr]["coverage_pct"].values
        if len(cov) == 0:
            continue
        fig.add_annotation(
            x=yr,
            y=cov[0],
            text=event["label"],
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor="#94a3b8",
            ax=0,
            ay=-40,
            font=dict(size=11, color=theme["text"]),
            bgcolor=theme["card_bg"],
            bordercolor=theme["card_border"],
            borderwidth=1,
            borderpad=4,
        )

fig.update_layout(
    template=theme["plotly_template"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=440,
    margin=dict(l=40, r=20, t=20, b=40),
    xaxis=dict(
        title="Year",
        gridcolor=theme["card_border"],
        dtick=2,
    ),
    yaxis=dict(
        title="Coverage (%)",
        gridcolor=theme["card_border"],
        range=[0, 50],
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    hovermode="x unified",
)

st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------------
# Interpretation
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️  Understanding incidental coverage", expanded=False):
    st.markdown("""
    **What this metric measures:** The fraction of grid cells classified as
    "high suitability" for anchovy (≥ 0.5 probability) that happen to fall
    inside *any* existing marine closure — MPA, CCA, or RCA.

    **Why "incidental"?** None of these closures were designed with anchovy in
    mind. MPAs target habitat biodiversity, CCAs were created for cowcod
    recovery, and RCAs protect overfished rockfish. Any protection they offer
    to anchovy spawning habitat is a byproduct, not a goal.

    **Key observations (mock data):**
    - Coverage dropped sharply during the 2009-2011 anchovy crash, when habitat
      contracted to areas with less closure overlap
    - The long-term trend shows modest increase, driven partly by new MPA
      designations and partly by habitat shifts
    - Even at peak, less than half of high-suitability habitat receives any
      spatial protection

    > ⚠️ **Mock data** — values are synthetic. Real coverage metrics will be
    > computed from Model B outputs overlaid on NOAA closure shapefiles.
    """)
