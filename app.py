"""
Northern Anchovy Spatial Conservation Framework
================================================
Main dashboard entry point — Historical Habitat Map view.

This is the home page. It displays a Folium heatmap of anchovy habitat
suitability over the California Current with a year slider and closure
polygon overlays.
"""

import streamlit as st
import plotly.graph_objects as go
from streamlit_folium import st_folium
from utils.constants import YEAR_MIN, YEAR_MAX, THEMES
from utils.model_data import generate_habitat_grid, generate_coverage_timeseries
from utils.map_utils import build_habitat_map
from utils.gfw_data import get_annual_effort, get_closure_effort, CACHED_ANNUAL_EFFORT

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Anchovy Conservation Framework",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Theme management
# ---------------------------------------------------------------------------
def get_theme() -> str:
    """Return the current theme name from session state."""
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
    return st.session_state.theme


def inject_custom_css(theme_name: str):
    """Inject CSS overrides for the selected theme."""
    t = THEMES[theme_name]
    st.markdown(f"""
    <style>
        /* ---- Global overrides ---- */
        .stApp {{
            background-color: {t["bg"]};
            color: {t["text"]};
        }}



        /* Force text color on ALL Streamlit elements */
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp li, .stApp td, .stApp th, .stApp caption, .stApp strong, .stApp em, .stApp a,
        .stApp .stMarkdown, .stApp .stMarkdown p,
        .stApp .stMarkdown li, .stApp .stMarkdown span,
        .stApp [data-testid="stText"],
        .stApp [data-testid="stCaptionContainer"],
        .stApp [data-testid="stCaptionContainer"] p,
        .stApp [data-testid="stCaptionContainer"] span,
        .stApp [data-testid="stMarkdownContainer"],
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] span,
        .stApp [data-testid="stMarkdownContainer"] li,
        .stApp [data-testid="stMarkdownContainer"] h1,
        .stApp [data-testid="stMarkdownContainer"] h2,
        .stApp [data-testid="stMarkdownContainer"] h3,
        .stApp [data-testid="stMarkdownContainer"] h4,
        .stApp [data-testid="stMarkdownContainer"] td,
        .stApp [data-testid="stMarkdownContainer"] th,
        .stApp [data-testid="stMarkdownContainer"] strong,
        .stApp [data-testid="stWidgetLabel"] p,
        .stApp [data-testid="stWidgetLabel"] label,
        .stApp .stRadio label,
        .stApp .stCheckbox label,
        .stApp .stSlider label {{
            color: {t["text"]} !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {t["bg_secondary"]};
        }}
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] h5,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] strong,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stCheckbox label {{
            color: {t["text"]} !important;
        }}

        /* ---- Metric cards ---- */
        .metric-card {{
            background: {t["card_bg"]};
            border: 1px solid {t["card_border"]};
            border-radius: 12px;
            padding: 24px 28px;
            text-align: center;
        }}
        .metric-card .metric-value {{
            font-size: 2.8rem;
            font-weight: 700;
            color: {t["accent"]} !important;
            line-height: 1.1;
        }}
        .metric-card .metric-label {{
            font-size: 0.9rem;
            color: {t["text"]} !important;
            opacity: 0.7;
            margin-top: 6px;
        }}

        /* ---- Hero header ---- */
        .hero-title {{
            font-size: 2rem;
            font-weight: 800;
            color: {t["accent"]} !important;
            margin-bottom: 0;
            padding: 0;
        }}
        .hero-subtitle {{
            font-size: 1.05rem;
            opacity: 0.7;
            margin-top: 4px;
            color: {t["text"]} !important;
        }}

        /* ---- Misc polish ---- */
        .block-container {{
            padding-top: 3rem;
        }}

        /* ---- Slider: blue thumb, gray track ---- */
        .stSlider [data-testid="stThumbValue"] {{
            color: {t["text"]} !important;
        }}
        .stSlider [role="slider"] {{
            background-color: {t["accent"]} !important;
        }}
        .stSlider [data-baseweb="slider"] div[role="slider"] {{
            background-color: {t["accent"]} !important;
            border-color: {t["accent"]} !important;
        }}
        /* Track (filled portion) */
        .stSlider [data-baseweb="slider"] div:nth-child(3) > div {{
            background-color: {t["accent"]} !important;
        }}
        /* Track (unfilled portion) */
        .stSlider [data-baseweb="slider"] div:nth-child(4) > div {{
            background-color: #94a3b8 !important;
        }}
        /* Fallback slider overrides */
        .stSlider > div > div > div > div {{
            background-color: #94a3b8 !important;
        }}
        .stSlider > div > div > div > div > div {{
            background-color: {t["accent"]} !important;
        }}

        /* ---- Expander / details text ---- */
        .stApp details,
        .stApp details summary,
        .stApp details summary span,
        .stApp details summary svg,
        .stApp details > div,
        .stApp details p, .stApp details li,
        .stApp details span, .stApp details blockquote,
        .stApp details blockquote p,
        .stApp details strong, .stApp details em,
        .stApp [data-testid="stExpander"],
        .stApp [data-testid="stExpander"] p,
        .stApp [data-testid="stExpander"] li,
        .stApp [data-testid="stExpander"] span,
        .stApp [data-testid="stExpander"] strong {{
            color: {t["text"]} !important;
        }}

        /* ---- Map legend ---- */
        .map-legend {{
            display: flex;
            gap: 6px;
            align-items: center;
            margin-top: 8px;
        }}
        .legend-swatch {{
            width: 18px;
            height: 12px;
            border-radius: 2px;
            display: inline-block;
        }}
        .legend-label {{
            font-size: 0.75rem;
            opacity: 0.7;
            color: {t["text"]} !important;
        }}
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
theme = get_theme()

with st.sidebar:
    st.markdown("### 🐟 Anchovy Conservation")
    st.markdown("##### Spatial Framework for the California Current")
    st.divider()



    st.divider()

    # Year slider
    selected_year = st.slider(
        "Select Year",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=YEAR_MAX,
        step=1,
    )

    show_closures = st.checkbox("Show Conservation Closures", value=True)
    show_fishing = st.checkbox("Show Fishing Pressure", value=False)

    st.divider()

    # Legend
    st.markdown("**Habitat Suitability**")
    st.markdown("""
    <div class="map-legend">
        <span class="legend-swatch" style="background:#164e63"></span>
        <span class="legend-label">Low</span>
        <span class="legend-swatch" style="background:#0e7490"></span>
        <span class="legend-swatch" style="background:#06b6d4"></span>
        <span class="legend-label">Med</span>
        <span class="legend-swatch" style="background:#fbbf24"></span>
        <span class="legend-swatch" style="background:#ef4444"></span>
        <span class="legend-label">High</span>
    </div>
    """, unsafe_allow_html=True)

    if show_closures:
        st.markdown("**Closure Types**")
        st.markdown("""
        <div class="map-legend">
            <span class="legend-swatch" style="background:#f59e0b"></span>
            <span class="legend-label">GEA (Groundfish Essential Area)</span>
        </div>
        """, unsafe_allow_html=True)

    if show_fishing:
        st.markdown("**Fishing Pressure**")
        st.markdown("""
        <div class="map-legend">
            <span class="legend-swatch" style="background:#22c55e; border-radius:50%"></span>
            <span class="legend-label">GEA: no fishing detected</span>
        </div>
        <div class="map-legend">
            <span class="legend-swatch" style="background:#f97316; border-radius:50%"></span>
            <span class="legend-label">Fleet operating zone</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.caption("Data: CalCOFI CUFES · NOAA · XGBoost")


# ---------------------------------------------------------------------------
# Apply theme CSS
# ---------------------------------------------------------------------------
inject_custom_css(st.session_state.theme)


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown('<p class="hero-title">Historical Anchovy Habitat</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="hero-subtitle">Modeled suitability across the California Current · {selected_year}</p>',
    unsafe_allow_html=True,
)

# Load fishing data (cached — no API calls at runtime)
closure_effort = get_closure_effort()
annual_effort = get_annual_effort()

# Generate habitat data & build map
grid = generate_habitat_grid(selected_year)
habitat_map = build_habitat_map(
    grid,
    theme_name=st.session_state.theme,
    show_closures=show_closures,
    show_fishing=show_fishing,
    closure_effort=closure_effort,
    annual_effort=annual_effort,
)

# Display map
st_folium(habitat_map, width="stretch", height=560, returned_objects=[])

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
coverage_ts = generate_coverage_timeseries()
current_coverage = coverage_ts[coverage_ts["year"] == selected_year]["coverage_pct"].values[0]
avg_coverage = coverage_ts["coverage_pct"].mean()
high_hab_cells = (grid["suitability"] >= 0.2).sum()
total_cells = len(grid)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{current_coverage:.1f}%</div>
        <div class="metric-label">High-suitability habitat<br>inside any closure ({selected_year})</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_coverage:.1f}%</div>
        <div class="metric-label">Average incidental coverage<br>{YEAR_MIN}–{YEAR_MAX}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{high_hab_cells}/{total_cells}</div>
        <div class="metric-label">Grid cells with ≥ 20%<br>suitability in {selected_year}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Combined: Habitat coverage vs. fishing effort (2016–2022)
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### Three-Layer Analysis: Habitat · Closures · Fishing Pressure")
st.markdown(
    '<p style="opacity:0.65; font-size:0.95rem;">How do the three layers relate over time? '
    'If fishing effort tracks habitat availability, spatial management could make a difference.</p>',
    unsafe_allow_html=True,
)

# Build shared year range
import pandas as pd
coverage_ts = generate_coverage_timeseries()
overlap_years = sorted(set(annual_effort.keys()) & set(coverage_ts["year"].tolist()))
overlap_years = [y for y in overlap_years if y >= 2016]

cov_vals = [coverage_ts[coverage_ts["year"] == y]["coverage_pct"].values[0] for y in overlap_years]
effort_vals = [annual_effort.get(y, 0) for y in overlap_years]

t = THEMES[st.session_state.theme]
fig_combined = go.Figure()

# Bars: fishing effort (right axis)
fig_combined.add_trace(go.Bar(
    x=overlap_years, y=effort_vals,
    name="Purse seiner effort (hrs)",
    marker_color="#f97316",
    marker_opacity=0.75,
    yaxis="y2",
    hovertemplate="<b>%{x}</b><br>Fishing: %{y:.0f} hrs<extra></extra>",
))

# Line: incidental coverage (left axis)
fig_combined.add_trace(go.Scatter(
    x=overlap_years, y=cov_vals,
    name="Incidental coverage (%)",
    line=dict(color=t["accent"], width=2.5),
    mode="lines+markers",
    marker=dict(size=7),
    yaxis="y1",
    hovertemplate="<b>%{x}</b><br>Coverage: %{y:.1f}%<extra></extra>",
))

fig_combined.update_layout(
    template=t["plotly_template"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=320,
    margin=dict(l=50, r=60, t=20, b=40),
    hovermode="x unified",
    bargap=0.35,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(title="Year", gridcolor=t["card_border"], dtick=1),
    yaxis=dict(
        title="Incidental coverage (%)",
        gridcolor=t["card_border"],
        titlefont=dict(color=t["accent"]),
        tickfont=dict(color=t["accent"]),
    ),
    yaxis2=dict(
        title="Vessel-hours fished",
        overlaying="y", side="right",
        titlefont=dict(color="#f97316"),
        tickfont=dict(color="#f97316"),
        showgrid=False,
    ),
)
st.plotly_chart(fig_combined, use_container_width=True)

st.markdown(f"""
<div style="background:{t['card_bg']}; border-left:3px solid {t['accent']};
     border-radius:8px; padding:14px 18px; margin-top:4px; font-size:0.9rem;">
    <strong>What this shows:</strong> Purse seiner effort (orange bars) and the fraction of
    anchovy habitat inside closures (blue line) are plotted together. The fleet peaked at
    <strong>307 hrs in 2017</strong> — after the warm blob disrupted habitat in 2015–2016.
    Zero fishing was detected inside any GEA closure across all years, while the broader
    region saw up to 307 vessel-hours of effort. The closures offer
    <em>incidental habitat overlap but zero pressure reduction</em> — the fleet operates
    entirely in unprotected coastal waters.
</div>
""", unsafe_allow_html=True)
st.markdown("")

# ---------------------------------------------------------------------------
# Context blurb
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️  About this view", expanded=False):
    st.markdown("""
    **What you're seeing:** A 0.5° gridded estimate of anchovy habitat
    suitability predicted by an XGBoost classifier trained on CUFES
    (Continuous Underway Fish Egg Sampler) data matched with environmental
    conditions (temperature, salinity, month, location).

    **Closure overlays** show Groundfish Essential Areas (GEAs) from the
    Federal Register (90 FR 57719). These closures were designed for
    groundfish conservation — any protection they provide to anchovy
    habitat is *incidental*.

    **Use the year slider** to see how habitat distribution has shifted
    across the 1996–2022 sampling period.
    """)
