"""
Scenario Explorer — Warming scenario visualization page.

Shows how anchovy habitat distribution and closure overlap change
under +0.5°C / +1°C / +2°C warming assumptions.
"""

import streamlit as st
from streamlit_folium import st_folium
from utils.constants import THEMES, SCENARIOS, YEAR_MAX
from utils.model_data import (
    generate_habitat_grid,
    generate_scenario_grid,
    compute_scenario_coverage,
    generate_coverage_timeseries,
)
from utils.map_utils import build_habitat_map

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
        .block-container {{ padding-top: 3rem; }}
        .scenario-delta-positive {{
            color: #ef4444 !important; font-weight: 700;
        }}
        .scenario-delta-negative {{
            color: #10b981 !important; font-weight: 700;
        }}
        .scenario-badge {{
            display: inline-block;
            background: {t["card_bg"]};
            border: 1px solid {t["card_border"]};
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 0.85rem;
            color: {t["text"]} !important;
            margin-right: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)


inject_page_css(theme)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌡️ Scenario Explorer")
    st.divider()

    scenario_label = st.radio(
        "Warming Scenario",
        options=list(SCENARIOS.keys()),
        index=0,
    )
    scenario_delta = SCENARIOS[scenario_label]

    show_closures = st.checkbox("Show Conservation Closures", value=True)

    st.divider()
    st.markdown("""
    **How to read this:**
    Select a warming scenario to see how habitat
    suitability shifts. These are *not forecasts* —
    they show model output under assumed temperature
    changes applied uniformly.
    """)

    st.divider()

    # Legend
    st.markdown("**Habitat Suitability**")
    st.markdown("""
    <div style="display:flex;gap:6px;align-items:center;margin-top:8px">
        <span style="width:18px;height:12px;border-radius:2px;display:inline-block;background:#164e63"></span>
        <span style="font-size:0.75rem;opacity:0.7">Low</span>
        <span style="width:18px;height:12px;border-radius:2px;display:inline-block;background:#06b6d4"></span>
        <span style="font-size:0.75rem;opacity:0.7">Med</span>
        <span style="width:18px;height:12px;border-radius:2px;display:inline-block;background:#ef4444"></span>
        <span style="font-size:0.75rem;opacity:0.7">High</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("⚠️ Scenarios, not forecasts")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown('<p class="hero-title">Scenario Explorer</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="hero-subtitle">Habitat distribution under {scenario_label}</p>',
    unsafe_allow_html=True,
)

# Badges
st.markdown(f"""
<div style="margin: 8px 0 16px 0">
    <span class="scenario-badge">🌡️ {scenario_label}</span>
    <span class="scenario-badge">📅 Baseline: {YEAR_MAX}</span>
    <span class="scenario-badge">🗺️ California Current</span>
</div>
""", unsafe_allow_html=True)

# Generate data
if scenario_delta == 0.0:
    grid = generate_habitat_grid(YEAR_MAX)
else:
    grid = generate_scenario_grid(scenario_delta)

# Build and show map
habitat_map = build_habitat_map(
    grid,
    theme_name=st.session_state.theme,
    show_closures=show_closures,
    layer_name=f"Habitat ({scenario_label})",
)

st_folium(habitat_map, width="stretch", height=520, returned_objects=[])

# ---------------------------------------------------------------------------
# Comparison metrics
# ---------------------------------------------------------------------------
baseline_coverage_row = generate_coverage_timeseries()
baseline_coverage = baseline_coverage_row[
    baseline_coverage_row["year"] == YEAR_MAX
]["coverage_pct"].values[0]

if scenario_delta == 0.0:
    scenario_coverage = baseline_coverage
else:
    scenario_coverage = compute_scenario_coverage(scenario_delta)

delta = scenario_coverage - baseline_coverage
delta_class = "scenario-delta-negative" if delta < 0 else "scenario-delta-positive"
delta_arrow = "↓" if delta < 0 else "↑"
delta_sign = "+" if delta >= 0 else ""

baseline_high = (generate_habitat_grid(YEAR_MAX)["suitability"] >= 0.2).sum()
scenario_high = (grid["suitability"] >= 0.2).sum()
hab_delta = scenario_high - baseline_high

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{scenario_coverage:.1f}%</div>
        <div class="metric-label">Projected coverage<br>under {scenario_label}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">
            <span class="{delta_class}">{delta_arrow} {delta_sign}{delta:.1f}%</span>
        </div>
        <div class="metric-label">Change from<br>2024 baseline ({baseline_coverage:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    hab_arrow = "↓" if hab_delta < 0 else "↑"
    hab_class = "scenario-delta-negative" if hab_delta < 0 else "scenario-delta-positive"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">
            <span class="{hab_class}">{hab_arrow} {hab_delta:+d}</span>
        </div>
        <div class="metric-label">High-suitability cells<br>vs. baseline ({baseline_high})</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️  About scenario projections", expanded=False):
    st.markdown("""
    **What this is:** The habitat model (Model B) applied to current
    environmental conditions with a uniform temperature increment added.

    **What this is NOT:** A climate forecast. Real projections require
    dynamically downscaled CMIP models (e.g., ROMS) that simulate changes
    in currents, upwelling, salinity, and stratification — not just temperature.

    **Why we show it anyway:** It demonstrates the *framework*. If institutions
    with production ocean models (Scripps, NOAA SWFSC) adopted this approach,
    they could run the same analysis with physically consistent future states.

    **Interpretation:**
    - As warming increases, the model shifts peak habitat suitability northward
    - Southern closures (CCAs) may lose some of their incidental anchovy coverage
    - Northern areas (Cordell Bank, Gulf of Farallones) may see increased overlap
    - Magnitude of effects is assumption-dependent and should not be taken literally
    """)
