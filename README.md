# Spatial Conservation Framework for Northern Anchovy

**Hackathon Project Plan**

| | |
|---|---|
| **Timeline** | 18 hours |
| **Tracks** | ML/AI + Data Analytics (same project, two pitch framings) |
| **Species focus** | Northern anchovy (*Engraulis mordax*) |
| **Region** | California Current |

---

## The One-Paragraph Pitch

Northern anchovies are the foundation of the California Current ecosystem — brown pelicans, sea lions, humpback whales, and Chinook salmon all depend on them. In 2009-2011, anchovy populations crashed 99% (from ~1 million tons to 15,000 tons) in the near-absence of fishing pressure. Sea lion pups starved on California beaches. Brown pelicans abandoned their nests. In 2022, a federal court ruled that NOAA had violated fishery law by managing anchovy with decades-old data. Today, anchovy management is entirely catch-limit-based — no spatial protections exist for this keystone forage species. We built a framework for thinking about anchovy conservation spatially: where is suitable habitat, how does it overlap with the existing closure network (designed for other species), and how might both shift under climate scenarios. We are not forecasting the ocean. We are proposing a methodology for a question no one is currently asking in a structured way.

## What We're NOT Claiming

Stating this first because it's what keeps the project defensible:

- We are **not** forecasting ocean conditions with production-grade accuracy
- We are **not** predicting anchovy populations
- We are **not** recommending specific closure boundaries
- We are **not** arguing spatial closures should replace catch limits
- We are **not** claiming our tool is ready for policy use as-is

We are proposing a **framework**. Institutions like Scripps or NOAA, with better models and domain expertise, could scale this approach. What we contribute is the question, the proof of concept, and the honest evaluation of what's possible at our scale.

---

## The Three-Part Framework

### Part 1: Historical habitat modeling

Train a machine learning model on 27 years of CalCOFI larval anchovy data matched with environmental conditions (temperature, salinity, depth). The model learns: "what combinations of conditions correspond to high anchovy larval densities?" Output: a habitat suitability probability for any (lat, lon, time).

### Part 2: Incidental coverage analysis

Overlay modeled historical habitat onto existing West Coast closures (MPAs, Cowcod Conservation Areas, Rockfish Conservation Areas). None of these were designed for anchovy. Quantify: what fraction of high-suitability anchovy habitat falls inside any protected area? How has this changed from 1997 to today?

### Part 3: Scenario exploration

Apply simple temperature-increment scenarios (+0.5°C, +1°C, +2°C) to recent conditions. Run through the habitat model. Show how projected habitat distribution and closure overlap change. These are scenarios, not forecasts.

---

## Data Sources

| Dataset | Role | Access |
|---------|------|--------|
| CalCOFI ichthyoplankton database | Anchovy larval density labels | [calcofi.org/data](https://calcofi.org/data) |
| CalCOFI hydrographic data (CTD) | Coastal temperature/salinity — matched to larval samples | [calcofi.org/data](https://calcofi.org/data) |
| EasyOneArgo (SEANOE) | Offshore temperature/salinity, 1997-2026 | [seanoe.org](https://www.seanoe.org/data/00961/107233) |
| NOAA closure shapefiles | Existing West Coast closures (MPAs, CCAs, RCAs) | [fisheries.noaa.gov](https://www.fisheries.noaa.gov/west-coast) |

**Scope:** California Current only. Monthly aggregation on 0.5° grid. Anchovy only.

---

## ML Architecture

Two models, chained. The first is the real technical contribution; the second is a framework demonstration.

### Model B (the real ML work): Anchovy Habitat Model

| Component | Detail |
|-----------|--------|
| **Input features** | Temperature, salinity, depth, month, year, latitude, longitude |
| **Target** | Anchovy larval density from CalCOFI (log-transformed) or presence/absence |
| **Model** | Random Forest or XGBoost (interpretable, handles non-linearity, fast to train) |
| **Critical** | Use spatial cross-validation, not random splits. Hold out entire geographic regions for testing. |
| **Evaluation** | AUC or R² with spatial CV, feature importance plot, calibration curve |
| **Output** | Probability of suitable habitat for any (lat, lon, environmental conditions) |

### Model A (framework demonstration): Scenario Generator

| Component | Detail |
|-----------|--------|
| **Purpose** | Show what the framework looks like when fed hypothetical future conditions |
| **Approach** | Apply simple temperature deltas to recent state. Not a forecasting model. |
| **Framing** | "Under an assumed +1°C warming, here's where the habitat model places suitable habitat." |
| **Why this matters** | Sidesteps the extrapolation problem. We're explicit that production forecasting requires dynamically downscaled CMIP models, which we don't have. |

### The Pipeline

```
Historical environmental data → Model B → historical habitat map
Recent conditions + temperature delta → Model B → scenario habitat map
Both overlaid on NOAA closures → incidental coverage metric
```

---

## Dashboard Features

### Core MVP (must ship)

- **Historical map** — Anchovy habitat suitability over the California Current, with year slider (1997-2024). Existing closures overlaid as polygons.
- **Incidental coverage metric** — Time series chart: "% of high-suitability anchovy habitat inside any closure" from 1997 to today. Single headline number for "today."
- **Scenario view** — Same map layout, but showing habitat under +0.5°C / +1°C / +2°C warming scenarios. Scenario selector in sidebar.
- **Methodology tab** — First-class feature, not filler. Honest about what we built, what we didn't, what institutions would do differently.

### Stretch goals (only if ahead of schedule)

- Brown pelican / sea lion colony locations overlaid on habitat maps to visualize predator-prey spatial mismatch
- Random-placement baseline (what would overlap be if closures were random?)
- Fishing effort layer from Global Fishing Watch
- Pacific Decadal Oscillation phase as a scenario variable

### Explicitly cut

- Real ML forecasting model (replaced by scenario generator)
- Multi-species comparison (anchovy only)
- Fishing effort modeling
- Closure boundary recommendations
- Mobile responsiveness

---

## The Methodology Tab Specification

This tab is where rigor lives. It should include:

### What we built
- Data sources and time windows
- Model architecture (Model B in detail)
- Spatial cross-validation methodology
- Scenario generation approach

### Model performance
- Model B: AUC or R² with spatial CV confidence intervals
- Feature importance plot
- Calibration curve
- Comparison against persistence/climatology baselines

### What we explicitly didn't do
- Dynamical downscaling from CMIP climate models
- Biogeochemical coupling (chlorophyll, oxygen, pH)
- Larval drift / dispersal modeling
- Age-structured population dynamics
- Fishing pressure / effort modeling
- PDO regime cycle integration

### What production work would look like
- Scripps/NOAA have end-to-end models (ROMS + NPZ + individual-based fish models)
- Those models took years and millions of dollars; they're the right tool
- Our framework asks a question those models could answer at higher fidelity

### Confidence levels

| Level | Component | Rationale |
|-------|-----------|-----------|
| 🟢 **High** | Historical habitat maps | Trained on real data |
| 🟡 **Medium** | Present-day incidental coverage metric | Depends on model accuracy + closure data |
| 🔴 **Low** | Scenario projections | Assumption-dependent |

### What additional data would strengthen this
- CalCOFI egg counts (less dispersal than larvae)
- Fishing effort from AIS/VMS vessel tracking
- Acoustic survey biomass
- Satellite chlorophyll
- Predator colony productivity data

---

## Why Anchovy (Not Sardine or Rockfish)

**Why not cowcod/rockfish:** The Cowcod Conservation Areas worked. Cowcod recovered. Areas are being reopened in 2024 because of success. Our "drift" metric would measure something that demonstrably didn't prevent recovery — undermining our own pitch.

**Why not sardine:** Sardine crisis is real but ambient — fishery has been closed since 2015 and everyone knows it. The policy conversation is stable.

**Why anchovy:**
- **Active legal battle:** Federal court ruled against NOAA in 2022 for using 30-year-old data to set catch limits
- **Documented ecosystem cascade:** Brown pelican nesting failures 2010-2015; 70% of sea lion pups died before weaning in 2013-2014
- **Crash happened in near-absence of fishing:** Proves catch-limit-only management can't prevent environmental collapses
- **Strong spatial predator dependency:** Fixed-colony predators (pelicans on Channel Islands, sea lion rookeries) that can't follow fish if schools move
- **27-year assessment gap:** Formal stock assessments lapsed 1995-2022 — demonstrates value of alternative data-driven approaches

---

## Answering the Obvious Critiques

> **"Why not just use catch limits?"**
> Catch limits manage total extraction. They don't manage spatial ecosystem function. When anchovy concentrations shift away from pelican nesting colonies, the birds can't follow. A catch-limit regime that allows the quota to be filled anywhere geographically doesn't protect predator foraging ranges. We're not replacing catch limits — we're adding a spatial dimension they don't capture.

> **"Your coverage metric is incidental — you're measuring accidents."**
> That's exactly the point. Forage fish have no species-specific closures. The current protection network was never designed for them. Quantifying the accidental coverage is the first step in asking whether intentional spatial protection should be part of the toolkit.

> **"Sardines and anchovies naturally cycle — you can't separate climate change from the regime."**
> Correct. That's why we don't claim to. Our scenarios assume warming continues; PDO phase would be a separate variable a production model would handle. We're mapping habitat under environmental conditions, not predicting which conditions will occur.

> **"Your ML is extrapolating outside training data."**
> Model B isn't extrapolating — it's applied to environmental conditions that may be outside training range under scenarios. We acknowledge this is a limitation. We use scenario framing (not forecasting) specifically to be honest about this. Production models handle this with dynamical downscaling from physical climate models.

> **"Larvae aren't adults — you're modeling the wrong life stage."**
> We're modeling spawning/nursery habitat. Protecting spawning habitat is a recognized spatial management goal in its own right, not a workaround. Adult habitat would require different data (acoustic surveys) we don't have access to.

> **"Argo data is sparse in coastal zones."**
> Correct. We use CalCOFI's own bottle/CTD data (which samples right up to the coast) for coastal environmental features, and restrict Argo to offshore regions where it's appropriate. We report uncertainty separately for coastal vs offshore cells.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Data processing | Python, xarray, pandas, geopandas |
| ML | scikit-learn, XGBoost |
| Dashboard | Streamlit |
| Maps | Folium / Leaflet |
| Charts | Plotly |
| Deployment | Streamlit Community Cloud (or local) |

---

## Two Tracks, One Project

### ML/AI Track pitch (3 min)
1. Lead with Model B architecture and spatial cross-validation methodology
2. Show AUC/R², feature importance, baseline comparisons
3. Position scenario generator as framework demonstration
4. Demo dashboard briefly
5. Methodology tab as evidence of rigor

### Data Analytics Track pitch (3 min)
1. Lead with pelican/sea lion crisis and 2022 court ruling
2. "Nobody measures spatial forage fish protection — here's what it looks like when you do"
3. Demo dashboard primarily
4. Methodology tab as supporting evidence

*Same repo, same code, different opening frame.*

---

## Honest Risks

- **18 hours is tight.** Cut features ruthlessly at the hour-14 checkpoint.
- **Argo coastal sparsity** — mitigate with CalCOFI CTD data for coastal cells
- **Model B performance may be mediocre** — that's OK, we're demonstrating methodology, not claiming state-of-the-art. Report honest metrics.
- **Scenario generator may feel hand-wavy** — mitigate by being extremely clear it's not a forecast

---

## The One Thing That Saves Us

> Ship MVP by hour 14. Everything after that is polish and presentation. A clean, honest, scoped demo beats an ambitious broken one every time.

---

## Current Project Status & Updated Plan

*As of milestone check-in, the Core MVP is fully functional and successfully transitions from mock data to real ML outputs.*

### What is Complete:
1. **Model Integration:** `anchovy_xgb_model.pkl` is successfully tied into the backend (`utils/model_data.py`), generating real-time predictive habitat grids instead of synthetic noise.
2. **Coverage Analytics:** Built robust Shapely-based cell-intersection logic to accurately calculate incidental coverage overlaps. 
3. **Core UI/UX:** The dashboard looks premium. Dark/Light mode, map visualizations (Folium), time-series charts (Plotly), and Metric Cards are fully operational with real data scaling (1996–2022).
4. **Scenario Logic:** Built scenario functions that apply uniform thermal shifts to base feature matrices, dynamically generating "what-if" models.

### Proposed Next Steps & Additional Features:
Since the MVP is largely complete ahead of the "Hour 14" limit, we can begin shifting our focus towards the stretch goals that will provide a huge multiplier during our pitches:

1. **Populate Real Methodology Metrics:** Calculate the actual R², AUC, and feature importances for `anchovy_xgb_model.pkl` and inject them directly into the Methodology tab's info boxes.
2. **Visualize Predator-Prey Mismatch (High Priority Stretch Goal):** Plot fixed locations of known Channel Island brown pelican nesting colonies or sea lion rookeries over the Folium map. Seeing offshore suitable habitat shift away from fixed nearshore predators makes the "ecosystem cascade" point immediately visually obvious to judges.
3. **Random-Placement Baseline:** Generate a metric that compares current coverage to what overlap would look like if closure areas were distributed completely randomly. This explicitly answers: "Are current closures better than nothing for anchovies?"
4. **Deploy Application:** Test the app structure on Streamlit Community Cloud (via `requirements.txt`) so we have a live URL to drop into our presentations and share with judges.
