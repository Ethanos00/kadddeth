"""
Fishing Pressure — AIS-based purse seiner activity in anchovy habitat.

Data: Global Fishing Watch fishing effort (public-global-fishing-effort:v4.0)
Gear filter: purse_seines (primary gear for anchovy/sardine harvest)
Region: California Current (30–42°N, 116–126°W)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.constants import THEMES, KEY_EVENTS
from utils.gfw_data import get_annual_effort, get_closure_effort, CACHED_ANNUAL_EFFORT

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
theme = THEMES[st.session_state.theme]


def inject_css(t):
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t["bg"]}; color: {t["text"]}; }}
        section[data-testid="stSidebar"] {{ background-color: {t["bg_secondary"]}; }}
        .stApp header, .stApp [data-testid="stHeader"] {{ display: none !important; }}
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp li, .stApp td, .stApp th, .stApp strong, .stApp em,
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] li,
        .stApp [data-testid="stMarkdownContainer"] strong,
        .stApp [data-testid="stCaptionContainer"] p,
        .stApp [data-testid="stWidgetLabel"] p,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] strong {{
            color: {t["text"]} !important;
        }}
        .metric-card {{
            background: {t["card_bg"]}; border: 1px solid {t["card_border"]};
            border-radius: 12px; padding: 20px 24px; text-align: center;
        }}
        .metric-card .metric-value {{
            font-size: 2.4rem; font-weight: 700;
            color: {t["accent"]} !important; line-height: 1.1;
        }}
        .metric-card .metric-label {{
            font-size: 0.85rem; color: {t["text"]} !important;
            opacity: 0.7; margin-top: 6px;
        }}
        .finding-card {{
            background: {t["card_bg"]}; border-left: 3px solid {t["accent"]};
            border-radius: 8px; padding: 16px 20px; margin: 8px 0;
        }}
        .hero-title {{
            font-size: 2rem; font-weight: 800;
            color: {t["accent"]} !important; margin-bottom: 0;
        }}
        .hero-subtitle {{
            font-size: 1.05rem; opacity: 0.7;
            margin-top: 4px; color: {t["text"]} !important;
        }}
        .block-container {{ padding-top: 2rem; }}
    </style>
    """, unsafe_allow_html=True)


inject_css(theme)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚢 Fishing Pressure")
    st.divider()
    show_events = st.checkbox("Annotate key events", value=True)
    show_trend = st.checkbox("Show trend line", value=True)
    st.divider()
    st.caption("Source: Global Fishing Watch")
    st.caption("Gear: purse_seines")
    st.caption("Region: CA Current 30–42°N")
    st.caption("Period: 2012–2022")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="hero-title">Purse Seiner Fishing Pressure</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">AIS-detected fishing effort in Northern anchovy habitat — California Current</p>',
    unsafe_allow_html=True,
)
st.markdown("")

# ---------------------------------------------------------------------------
# Load data (uses cache, no API calls at runtime)
# ---------------------------------------------------------------------------
with st.spinner("Loading fishing effort data…"):
    annual = get_annual_effort()
    closure_effort = get_closure_effort()

df = pd.DataFrame({"year": list(annual.keys()), "hours": list(annual.values())})
df = df.sort_values("year").reset_index(drop=True)

peak_row = df.loc[df["hours"].idxmax()]
total_hours = df["hours"].sum()
active_years = (df["hours"] > 0).sum()
inside_closures = sum(closure_effort.values())

# ---------------------------------------------------------------------------
# Headline metrics
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
metrics = [
    (f"{total_hours:.0f} hrs", "Total effort 2012–2022"),
    (f"{peak_row['hours']:.0f} hrs", f"Peak year ({int(peak_row['year'])})"),
    (f"{active_years}/11", "Years with detected activity"),
    (f"{inside_closures:.0f} hrs", "Inside GEA closures"),
]
for col, (val, label) in zip([c1, c2, c3, c4], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("")

# ---------------------------------------------------------------------------
# Time series chart
# ---------------------------------------------------------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["year"], y=df["hours"],
    marker_color=theme["accent"],
    marker_opacity=0.8,
    name="Fishing hours",
    hovertemplate="<b>%{x}</b><br>%{y:.1f} vessel-hours<extra></extra>",
))

if show_trend:
    import numpy as np
    z = np.polyfit(df["year"], df["hours"], 1)
    trend = np.polyval(z, df["year"])
    fig.add_trace(go.Scatter(
        x=df["year"], y=trend,
        line=dict(color="#94a3b8", width=1.5, dash="dash"),
        mode="lines", name="Trend", hoverinfo="skip",
    ))

if show_events:
    for event in KEY_EVENTS:
        yr = event["year"]
        h = df.loc[df["year"] == yr, "hours"]
        if h.empty:
            continue
        fig.add_annotation(
            x=yr, y=h.values[0] + 15,
            text=event["label"], showarrow=True,
            arrowhead=2, arrowcolor="#94a3b8",
            ax=0, ay=-35,
            font=dict(size=10, color=theme["text"]),
            bgcolor=theme["card_bg"],
            bordercolor=theme["card_border"],
            borderwidth=1, borderpad=3,
        )

fig.update_layout(
    template=theme["plotly_template"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=380,
    margin=dict(l=40, r=20, t=20, b=40),
    xaxis=dict(title="Year", gridcolor=theme["card_border"], dtick=1),
    yaxis=dict(title="Vessel-hours fished", gridcolor=theme["card_border"]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    bargap=0.3,
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Per-closure bar chart
# ---------------------------------------------------------------------------
st.markdown("### Fishing Effort Inside GEA Closures (2016–2022)")

closure_df = pd.DataFrame({
    "closure": list(closure_effort.keys()),
    "hours": list(closure_effort.values()),
}).sort_values("hours", ascending=True)

if closure_df["hours"].sum() == 0:
    st.markdown(f"""
    <div class="finding-card">
        <strong>Key finding:</strong> Zero purse seiner activity detected inside any GEA closure
        during 2016–2022 — a period with {total_hours:.0f} total vessel-hours in the broader
        California Current region. The closures appear to be respected by the purse seine fleet,
        even though they were not designed to exclude pelagic fishing.
    </div>
    """, unsafe_allow_html=True)
else:
    fig2 = go.Figure(go.Bar(
        x=closure_df["hours"], y=closure_df["closure"],
        orientation="h",
        marker_color=theme["accent"], marker_opacity=0.8,
        hovertemplate="%{y}<br>%{x:.1f} vessel-hours<extra></extra>",
    ))
    fig2.update_layout(
        template=theme["plotly_template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=20, r=20, t=10, b=40),
        xaxis=dict(title="Vessel-hours", gridcolor=theme["card_border"]),
        yaxis=dict(gridcolor=theme["card_border"]),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Interpretation
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️  Understanding this analysis", expanded=False):
    st.markdown("""
    **What AIS tracks:** The Automatic Identification System (AIS) broadcasts vessel position,
    speed, and heading. Global Fishing Watch uses a neural network to classify when a vessel
    is actively fishing (vs. transiting) based on its movement pattern.

    **Why purse seiners?** Northern anchovy are primarily caught by purse seine vessels —
    large nets encircling a school of fish. Filtering AIS data to `geartype = purse_seines`
    isolates the fleet most likely to target anchovy (alongside sardine and mackerel).

    **Important caveat:** AIS cannot distinguish which species is being targeted.
    "Purse seiner effort in anchovy habitat" is a proxy — the same vessels may be targeting
    sardine or Pacific mackerel depending on market conditions.

    **Why zero inside closures?** The GEA (Groundfish Essential Areas) closures were created
    in 2025 to protect deep-sea coral and sponge habitat from bottom-contact gear. Purse seines
    are mid-water gear and are not technically prohibited inside GEAs — the zero reading
    suggests the closures happen to coincide with areas the purse seine fleet does not work
    (offshore banks, seamounts), not that the fleet is actively complying with a pelagic ban.

    **What the spike in 2017 means:** 2017 followed a period of anomalously warm water (the
    "Blob" through 2015–2016). As temperatures normalized, anchovy habitat may have
    concentrated in accessible areas, attracting more fleet effort.
    """)
