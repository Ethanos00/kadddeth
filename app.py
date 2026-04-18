"""
Northern Anchovy Spatial Conservation Framework
================================================
Main dashboard entry point — Historical Habitat Map view.

This is the home page. It displays a Folium heatmap of anchovy habitat
suitability over the California Current with a year slider and closure
polygon overlays.
"""

import streamlit as st
from streamlit_folium import st_folium
from utils.constants import YEAR_MIN, YEAR_MAX, THEMES
from utils.mock_data import generate_habitat_grid, generate_coverage_timeseries
from utils.map_utils import build_habitat_map

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
        st.session_state.theme = "Light"
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
        .stApp li, .stApp td, .stApp th, .stApp caption,
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
            background: linear-gradient(135deg, {t["accent"]}, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
            padding-top: 4px;
            line-height: 1.4;
            display: inline-block;
        }}
        .hero-subtitle {{
            font-size: 1.05rem;
            opacity: 0.7;
            margin-top: 4px;
            color: {t["text"]} !important;
        }}

        /* ---- Misc polish ---- */
        .block-container {{
            padding-top: 2rem;
        }}
        .stSlider > div > div > div > div {{
            background-color: {t["accent"]};
        }}

        /* ---- Expander text ---- */
        .stApp details summary span,
        .stApp details p, .stApp details li,
        .stApp details span, .stApp details blockquote p {{
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

    # Theme toggle
    theme_choice = st.radio(
        "Theme",
        options=["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1,
        horizontal=True,
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

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

    st.divider()
    st.caption("Data: CalCOFI · NOAA · EasyOneArgo")
    st.caption("⚠️ Mock data — model pipeline pending")


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

# Generate data & build map
grid = generate_habitat_grid(selected_year)
habitat_map = build_habitat_map(
    grid,
    theme_name=st.session_state.theme,
    show_closures=show_closures,
)

# Display map
st_folium(habitat_map, width="stretch", height=560, returned_objects=[])

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
coverage_ts = generate_coverage_timeseries()
current_coverage = coverage_ts[coverage_ts["year"] == selected_year]["coverage_pct"].values[0]
avg_coverage = coverage_ts["coverage_pct"].mean()
high_hab_cells = (grid["suitability"] >= 0.5).sum()
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
        <div class="metric-label">Grid cells with ≥ 50%<br>suitability in {selected_year}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Context blurb
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️  About this view", expanded=False):
    st.markdown("""
    **What you're seeing:** A 0.5° gridded estimate of anchovy habitat
    suitability, derived from environmental conditions (temperature, salinity,
    depth) matched to CalCOFI larval density records.

    **Closure overlays** show existing Marine Protected Areas (MPAs), Cowcod
    Conservation Areas (CCAs), and Rockfish Conservation Areas (RCAs). None of
    these closures were designed for anchovy — any protection they provide to
    anchovy habitat is *incidental*.

    **Use the year slider** to see how habitat distribution has shifted over
    time, particularly during the 2009-2011 population crash.

    > ⚠️ This is currently displaying **mock data** for UI development.
    > Real model outputs will replace these once the ML pipeline is complete.
    """)
