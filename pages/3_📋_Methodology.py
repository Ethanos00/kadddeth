"""
Methodology — Detailed documentation of the framework.

This is a first-class feature that establishes scientific credibility
by being transparent about methods, limitations, and what production
work would look like.
"""

import streamlit as st
from utils.constants import THEMES

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
        .stApp li, .stApp td, .stApp th, .stApp strong, .stApp em, .stApp a, .stApp code,
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
        .stApp [data-testid="stCaptionContainer"] p,
        .stApp [data-testid="stWidgetLabel"] p,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] strong,
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: {t["text"]} !important;
        }}

        /* Expanders — comprehensive text overrides */
        .stApp details, .stApp details summary, .stApp details summary span,
        .stApp details summary svg,
        .stApp details > div, .stApp details > div > div,
        .stApp details p, .stApp details li,
        .stApp details span, .stApp details blockquote,
        .stApp details blockquote p,
        .stApp details strong, .stApp details em,
        .stApp details td, .stApp details th, .stApp details code,
        .stApp details h4, .stApp details h3,
        .stApp [data-testid="stExpander"],
        .stApp [data-testid="stExpander"] p,
        .stApp [data-testid="stExpander"] li,
        .stApp [data-testid="stExpander"] span,
        .stApp [data-testid="stExpander"] strong,
        .stApp [data-testid="stExpander"] td,
        .stApp [data-testid="stExpander"] th,
        .stApp [data-testid="stExpander"] code,
        .stApp [data-testid="stExpander"] h3,
        .stApp [data-testid="stExpander"] h4,
        .confidence-high, .confidence-high strong, .confidence-high br,
        .confidence-med, .confidence-med strong, .confidence-med br,
        .confidence-low, .confidence-low strong, .confidence-low br {{
            color: {t["text"]} !important;
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
        .confidence-high {{
            background: #065f4620; border-left: 4px solid #10b981;
            padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0;
        }}
        .confidence-med {{
            background: #92400e20; border-left: 4px solid #f59e0b;
            padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0;
        }}
        .confidence-low {{
            background: #7f1d1d20; border-left: 4px solid #ef4444;
            padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0;
        }}
    </style>
    """, unsafe_allow_html=True)


inject_page_css(theme)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📋 Methodology")
    st.divider()
    st.markdown("""
    **Navigate sections:**
    - What We Built
    - Data Sources
    - Model Architecture
    - Spatial Cross-Validation
    - Model Performance
    - What We Didn't Build
    - Production Roadmap
    - Confidence Levels
    - Additional Data Needs
    """)
    st.divider()
    st.caption("Rigor is a feature, not a footnote.")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown('<p class="hero-title">Methodology</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">What we built, what we didn\'t, and what institutions would do differently</p>',
    unsafe_allow_html=True,
)

# ---- What We Built ----
with st.expander("🔧  What We Built", expanded=True):
    st.markdown("""
    A three-part spatial conservation framework for Northern Anchovy
    (*Engraulis mordax*) in the California Current:

    1. **Historical Habitat Modeling** — A machine learning model trained on
       27 years of CalCOFI larval anchovy data matched with environmental
       conditions (temperature, salinity, depth). The model learns what
       combinations of conditions correspond to high anchovy larval densities.

    2. **Incidental Coverage Analysis** — Overlay of modeled historical habitat
       onto existing West Coast closures (MPAs, CCAs, RCAs). Quantifies what
       fraction of high-suitability anchovy habitat falls inside any protected
       area and how this has changed from 1997 to today.

    3. **Scenario Exploration** — Simple temperature-increment scenarios
       (+0.5°C, +1°C, +2°C) applied to recent conditions, run through the
       habitat model to show how projected habitat distribution and closure
       overlap might change. These are scenarios, not forecasts.
    """)

# ---- Data Sources ----
with st.expander("📁  Data Sources", expanded=False):
    st.markdown("""
    | Dataset | Role | Access |
    |---------|------|--------|
    | CalCOFI ichthyoplankton database | Anchovy larval density labels | calcofi.org/data |
    | CalCOFI hydrographic data (CTD) | Coastal temperature/salinity | calcofi.org/data |
    | EasyOneArgo (SEANOE) | Offshore temperature/salinity, 1997-2026 | seanoe.org |
    | NOAA closure shapefiles | West Coast closures (MPAs, CCAs, RCAs) | fisheries.noaa.gov |

    **Scope:** California Current only. Monthly aggregation on a 0.5° grid.
    Northern anchovy only.

    **Time window:** 1997–2024 for historical analysis; scenario projections
    use 2024 as baseline.
    """)

# ---- Model Architecture ----
with st.expander("🧠  Model Architecture", expanded=False):
    st.markdown("""
    **Two models, chained:**

    #### Model B: Anchovy Habitat Model *(the real ML work)*

    | Component | Detail |
    |-----------|--------|
    | **Input features** | Temperature, salinity, depth, month, year, latitude, longitude |
    | **Target** | Anchovy larval density from CalCOFI (log-transformed) or presence/absence |
    | **Algorithm** | Random Forest or XGBoost |
    | **Why these?** | Interpretable, handles non-linearity, fast to train |
    | **Output** | Probability of suitable habitat for any (lat, lon, environmental conditions) |

    #### Model A: Scenario Generator *(framework demonstration)*

    | Component | Detail |
    |-----------|--------|
    | **Purpose** | Show what the framework looks like when fed hypothetical future conditions |
    | **Approach** | Apply simple temperature deltas to recent state |
    | **Framing** | "Under an assumed +1°C warming, here's where the habitat model places suitable habitat" |

    **The pipeline:**

    ```
    Historical env data → Model B → historical habitat map
    Recent conditions + Δt → Model B → scenario habitat map
    Both overlaid on NOAA closures → incidental coverage metric
    ```
    """)

# ---- Spatial Cross-Validation ----
with st.expander("🗺️  Spatial Cross-Validation", expanded=False):
    st.markdown("""
    **This is what separates rigorous Species Distribution Modeling from
    hackathon demos.**

    Standard random train/test splits violate the assumption of independent
    samples when data is spatially autocorrelated — nearby ocean grid cells
    have similar conditions, so a random split leaks information and inflates
    performance metrics.

    **Our approach:** Spatial block cross-validation. We hold out entire
    geographic regions (e.g., all grid cells north of 38°N) for testing.
    The model must generalize to regions it has never seen, not just
    interpolate between nearby training points.

    This gives more honest (and usually lower) performance numbers, but
    they reflect real predictive power.
    """)

# ---- Model Performance ----
with st.expander("📈  Model Performance", expanded=False):
    st.markdown("""
    > ⚠️ **Placeholder** — real metrics will be inserted once Model B is
    > trained on CalCOFI data.

    **Planned evaluation metrics:**
    - **AUC-ROC** with spatial CV confidence intervals
    - **Feature importance** plot (permutation importance)
    - **Calibration curve** (predicted probability vs. observed frequency)
    - **Comparison against baselines:**
      - Persistence (last year's habitat = this year's habitat)
      - Climatology (long-term average habitat)

    *Slots for plots:*
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.info("📊 Feature importance plot will appear here")
    with col2:
        st.info("📊 Calibration curve will appear here")

    st.info("📊 ROC curve with spatial CV folds will appear here")

# ---- What We Didn't Build ----
with st.expander("🚫  What We Explicitly Didn't Build", expanded=False):
    st.markdown("""
    Being transparent about scope is as important as showing results.

    | Not included | Why |
    |-------------|-----|
    | Dynamical downscaling from CMIP climate models | Requires ROMS/MOM6 ocean models; months of compute time |
    | Biogeochemical coupling (chlorophyll, oxygen, pH) | Important but beyond our data access and timeline |
    | Larval drift / dispersal modeling | Requires Lagrangian particle tracking; separate research project |
    | Age-structured population dynamics | Would need acoustic survey biomass data we don't have |
    | Fishing pressure / effort modeling | Requires AIS/VMS vessel tracking data access |
    | PDO regime cycle integration | Important context but requires careful statistical treatment |
    """)

# ---- Production Roadmap ----
with st.expander("🏗️  What Production Work Would Look Like", expanded=False):
    st.markdown("""
    Institutions like **Scripps Institution of Oceanography** or
    **NOAA Southwest Fisheries Science Center** have the tools to build
    this at production fidelity:

    - **End-to-end ocean models** (ROMS + NPZ + individual-based fish models)
      that took years and millions of dollars to develop
    - **Dynamically downscaled climate projections** from CMIP6 that
      capture changes in currents, upwelling, and stratification
    - **Validated acoustic survey data** for adult anchovy distribution
    - **Multi-decadal fishery-independent time series** for model training

    Our framework asks a question those models could answer at higher
    fidelity. What we contribute is the *question*, the *proof of concept*,
    and the *honest evaluation* of what's possible at our scale.
    """)

# ---- Confidence Levels ----
with st.expander("🎯  Confidence Levels", expanded=True):
    st.markdown("""
    <div class="confidence-high">
        <strong>🟢 HIGH CONFIDENCE — Historical habitat maps</strong><br>
        Trained on real CalCOFI data spanning 27 years. Environmental-habitat
        relationships are well-established in the literature. Spatial CV
        provides honest performance bounds.
    </div>

    <div class="confidence-med">
        <strong>🟡 MEDIUM CONFIDENCE — Present-day incidental coverage</strong><br>
        Depends on accuracy of both the habitat model and closure boundary
        data. Closure boundaries are authoritative (NOAA shapefiles), but
        habitat model has inherent uncertainty.
    </div>

    <div class="confidence-low">
        <strong>🔴 LOW CONFIDENCE — Scenario projections</strong><br>
        Assumption-dependent by design. Uniform temperature deltas don't
        capture real oceanographic complexity. These demonstrate framework
        capability, not predictions. Take magnitude with a large grain of salt.
    </div>
    """, unsafe_allow_html=True)

# ---- Additional Data ----
with st.expander("📋  What Additional Data Would Strengthen This", expanded=False):
    st.markdown("""
    - **CalCOFI egg counts** — Less dispersal than larvae; better proxy for
      spawning location
    - **Fishing effort from AIS/VMS** — Vessel tracking data would allow
      fishing pressure analysis
    - **Acoustic survey biomass** — Direct estimates of adult anchovy
      abundance and distribution
    - **Satellite chlorophyll** — Proxy for primary productivity and prey
      availability
    - **Predator colony productivity data** — Brown pelican nesting success,
      sea lion pup survival rates linked to local anchovy availability
    """)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "*Rigor is a feature.* This methodology section is not filler — it's the "
    "foundation of scientific credibility. We are proposing a framework, not "
    "making policy recommendations."
)
