"""
Smart Horticulture Advisor - Community Service Project
SVCET, Department of Information Technology

Run:   python -m streamlit run app.py
"""

import os
import datetime as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------
# Page configuration & Modern Styling
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Horticulture Advisor | SVCET Community Project",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load external CSS file if available, or fall back to inline
def load_css(css_file="style.css"):
    # Look for style.css in the script's directory or current working directory
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), css_file),
        os.path.join(os.getcwd(), css_file),
        css_file,
    ]
    for p in possible_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            return

load_css("style.css")

# Color Palette Constants
PRIMARY_GREEN = "#10B981"
DARK_GREEN = "#0F3E2E"
EMERALD = "#34D399"
ACCENT_AMBER = "#F59E0B"
ACCENT_RED = "#EF4444"
ACCENT_BLUE = "#3B82F6"

# ----------------------------------------------------------------------
# Core Domain Datasets
# ----------------------------------------------------------------------
SURVEY_PROBLEMS = pd.DataFrame(
    {
        "Problem": [
            "Crop pests & diseases", "Water scarcity", "Post-harvest storage loss",
            "No direct market access", "Excessive chemical usage", "Soil degradation",
        ],
        "Respondents (%)": [78, 66, 58, 52, 47, 41],
    }
)

RESPONDENTS = pd.DataFrame(
    {
        "Group": ["Small farmers (< 2 acres)", "Medium farmers (2-5 acres)", "Women agri-growers", "Local market vendors & consumers"],
        "Share": [45, 20, 15, 20],
    }
)

BEFORE_AFTER = pd.DataFrame(
    {
        "Skill": ["Knows residue risks", "Correct washing practices", "Can read pesticide safety labels"] * 2,
        "Stage": ["Pre-Workshop"] * 3 + ["Post-Workshop"] * 3,
        "Participants (%)": [35, 40, 22, 82, 85, 68],
    }
)

CROPS = {
    "Tomato":        {"ph": (6.0, 6.8), "temp": (20, 27), "n": "Medium to high", "water": "Regular, even moisture"},
    "Brinjal":       {"ph": (5.5, 6.8), "temp": (22, 30), "n": "Medium to high", "water": "Regular, avoid waterlogging"},
    "Leafy greens":  {"ph": (6.0, 7.0), "temp": (15, 25), "n": "High",           "water": "Frequent, light irrigation"},
    "Chilli":        {"ph": (6.0, 7.0), "temp": (20, 30), "n": "Medium",         "water": "Moderate"},
    "Okra":          {"ph": (6.0, 7.0), "temp": (24, 35), "n": "Medium",         "water": "Moderate"},
    "Guava":         {"ph": (5.5, 7.5), "temp": (23, 30), "n": "Low to medium",  "water": "Low once established"},
    "Banana":        {"ph": (5.5, 7.0), "temp": (26, 33), "n": "High",           "water": "High, steady supply"},
    "Marigold":      {"ph": (6.0, 7.5), "temp": (18, 30), "n": "Low to medium",  "water": "Moderate"},
}
N_LEVEL_RANK = {"Low": 1, "Medium": 2, "High": 3}

DISEASES = [
    {
        "crops": ["Tomato", "Brinjal", "Chilli"],
        "symptoms": {"Brown spots with yellow rings on leaves", "Leaves yellow from the bottom up"},
        "cause": "Early Blight (Fungal pathogen: Alternaria solani)",
        "advice": "Remove affected lower foliage, avoid overhead splash irrigation, ensure crop rotation, and enhance plant spacing. Apply registered copper fungicide or biological trichoderma if severe.",
    },
    {
        "crops": ["Tomato", "Brinjal", "Chilli", "Okra"],
        "symptoms": {"Leaves curl upward", "Tiny white insects under leaves", "Sticky leaf surface"},
        "cause": "Whitefly / Aphid Infestation (Vector of Leaf Curl Virus)",
        "advice": "Install bright yellow sticky traps (10-12 traps/acre), spray 5% neem seed kernel extract (NSKE) or systemic organic biopesticide, and clear alternate weed hosts surrounding fields.",
    },
    {
        "crops": ["Tomato", "Brinjal", "Chilli", "Okra", "Leafy greens"],
        "symptoms": {"Sudden wilting of whole plant", "Stem base dark or soft"},
        "cause": "Bacterial / Fusarium Wilt (Soil-borne pathogen)",
        "advice": "Improve drainage channels immediately to prevent stagnant water, uproot and safely destroy infected plants, avoid Solanaceous crops in the same plot, and adopt soil solarisation.",
    },
    {
        "crops": ["Brinjal", "Tomato", "Chilli"],
        "symptoms": {"Holes in fruit", "Drooping shoot tips"},
        "cause": "Shoot and Fruit Borer (Leucinodes orbonalis)",
        "advice": "Clip and discard drooping shoot tips regularly, set up sex pheromone traps (4-5 per acre), and maintain periodic clean harvests.",
    },
    {
        "crops": ["Guava", "Banana", "Marigold", "Leafy greens", "Tomato", "Brinjal", "Chilli", "Okra"],
        "symptoms": {"Powdery white coating on leaves"},
        "cause": "Powdery Mildew (Fungal)",
        "advice": "Prune overcrowded foliage to maximize sunlight and air circulation, avoid damp overhead watering, and spray wettable sulfur or bio-fungicide according to label instructions.",
    },
    {
        "crops": ["Guava", "Banana"],
        "symptoms": {"Dark scabby spots on fruit", "Fruit cracking or deformed"},
        "cause": "Fruit Scab / Anthracnose / Fruit Fly Attack",
        "advice": "Bag young fruits with protective covers, collect and bury fallen fruits, prune dead twigs, and deploy methyl eugenol fruit-fly traps.",
    },
    {
        "crops": ["Leafy greens", "Marigold", "Okra"],
        "symptoms": {"Leaves yellow overall", "Slow, stunted growth"},
        "cause": "Nutrient Deficiency (Nitrogen / Micronutrients)",
        "advice": "Incorporate well-composted farmyard manure, vermicompost, or balanced organic biofertilizer (Azotobacter). Conduct a comprehensive soil test.",
    },
]
ALL_SYMPTOMS = sorted({s for d in DISEASES for s in d["symptoms"]})

def _sample_prices() -> pd.DataFrame:
    base = {"Tomato": 22, "Brinjal": 28, "Leafy greens": 18, "Chilli": 55, "Okra": 35, "Guava": 40, "Banana": 32, "Marigold": 60}
    rows = []
    today = dt.date.today()
    for i, day in enumerate(pd.date_range(today - dt.timedelta(days=29), today)):
        for crop, p in base.items():
            wave = ((i * 7 + len(crop) * 3) % 11 - 5) * 0.03
            weekend = 0.05 if day.weekday() in (5, 6) else 0.0
            rows.append({"Date": day, "Crop": crop, "Price (Rs/kg)": round(p * (1 + wave + weekend), 1)})
    return pd.DataFrame(rows)

PRICE_DATA = _sample_prices()

WASH_GUIDE = {
    "Tomato": [
        "Rinse under lukewarm running potable water for at least 30-45 seconds.",
        "Gently rub the skin and calyx/stem junction with hands or a clean soft produce brush.",
        "Pat dry with clean cotton paper towels before storing or eating."
    ],
    "Brinjal": [
        "Hold under running water for 30 seconds to wash off surface dust and residues.",
        "Gently brush around the prickly cap/stem where spray residues collect.",
        "Dry with a clean towel; keep dry before chilling."
    ],
    "Leafy greens": [
        "Separate leaves and discard wilted outer layers.",
        "Immerse and agitate in cool clean water for 2 minutes to dislodge silt.",
        "Optional: soak in 2% salt or mild baking soda/vinegar solution for 5 mins, followed by fresh water rinse.",
        "Spin in salad spinner or shake thoroughly and air-dry."
    ],
    "Guava & Apple": [
        "Rinse thoroughly under running tap water.",
        "Rub the textured surface with clean hands or a soft brush.",
        "Peel lightly only if heavy non-food grade wax coatings are present; otherwise retain nutrient-rich skin."
    ],
    "Cucumber & Okra": [
        "Wash each piece under clean running water, rubbing the ridges gently.",
        "Trim the stem ends only after washing to prevent interior water absorption.",
        "Pat thoroughly dry before cutting."
    ],
}

def show(fig):
    """Safely render Plotly chart with modern styling and responsive width."""
    fig.update_layout(
        font_family="Plus Jakarta Sans, sans-serif",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E2E8F0",
    )
    try:
        st.plotly_chart(fig, use_container_width=True)
    except TypeError:
        st.plotly_chart(fig)

# ----------------------------------------------------------------------
# Business Logic
# ----------------------------------------------------------------------
def score_crop(crop: str, ph: float, temp: float, nitrogen: str, water: str):
    req = CROPS[crop]
    score, notes = 0, []

    lo, hi = req["ph"]
    if lo <= ph <= hi:
        score += 40
        notes.append(f"Soil pH {ph:.1f} is optimal ({lo}–{hi}).")
    else:
        gap = min(abs(ph - lo), abs(ph - hi))
        score += max(0, 40 - int(gap * 20))
        remedy = "Apply agricultural lime / dolomite cautiously." if ph < lo else "Incorporate organic compost, gypsum, or elemental sulfur."
        notes.append(f"Soil pH {ph:.1f} deviates from ideal range ({lo}–{hi}). {remedy}")

    tlo, thi = req["temp"]
    if tlo <= temp <= thi:
        score += 30
        notes.append(f"Temperature {temp:.1f}°C matches this crop's growth cycle ({tlo}–{thi}°C).")
    else:
        gap = min(abs(temp - tlo), abs(temp - thi))
        score += max(0, 30 - int(gap * 4))
        notes.append(f"Temperature {temp:.1f}°C is outside standard range ({tlo}–{thi}°C). Use shade nets or schedule sowing strategically.")

    need = req["n"].split(" ")[0]
    have = N_LEVEL_RANK[nitrogen]
    want = N_LEVEL_RANK.get(need, 2)
    if have >= want:
        score += 20
        notes.append(f"Nitrogen availability ({nitrogen}) is sufficient for standard vegetative yield.")
    else:
        score += 8
        notes.append("Nitrogen appears inadequate. Supplement with vermicompost, cow dung manure, or green leaf manuring.")

    water_ok = {"Low": 1, "Moderate": 2, "Plenty": 3}[water]
    need_w = 3 if req["water"].startswith("High") else (1 if req["water"].startswith("Low") else 2)
    if water_ok >= need_w:
        score += 10
        notes.append("Irrigation capacity matches plant evapotranspiration needs.")
    else:
        notes.append("Water supply is constrained. Adopt drip irrigation, mulching, and night watering.")

    return min(score, 100), notes


def soil_water_report(ph: float, nitrogen: str, temp: float, water: str):
    items = []
    if ph < 5.5:
        items.append(("Strongly Acidic Soil", "Most horticultural vegetables struggle with phosphorus tie-up. Apply agricultural lime after soil test.", "bad"))
    elif ph < 6.0:
        items.append(("Moderately Acidic Soil", "Acceptable for brinjal, guava, and banana. Consider slight liming for leafy vegetables.", "warn"))
    elif ph <= 7.5:
        items.append(("Optimal Soil pH", "Excellent nutrient availability for nearly all vegetables and fruit crops.", "ok"))
    elif ph <= 8.0:
        items.append(("Moderately Alkaline Soil", "Risk of micronutrient deficiency (zinc, iron). Add organic farmyard manure.", "warn"))
    else:
        items.append(("Strongly Alkaline / Saline Soil", "High risk of salt injury. Treat with gypsum and improve subsoil leaching.", "bad"))

    if nitrogen == "Low":
        items.append(("Nitrogen Deficiency", "Causes chlorosis and stunted growth. Boost with vermicompost or legumes.", "warn"))
    else:
        items.append((f"{nitrogen} Nitrogen Level", "Sufficient vegetative support. Avoid excessive chemical nitrogen to prevent aphid outbreaks.", "ok"))

    if temp > 38:
        items.append(("Thermal Heat Stress", "High flower drop rate. Irrigate in early dawn/evening and install 50% shade nets.", "bad"))
    elif temp < 12:
        items.append(("Cold / Frost Stress", "Stunts germination and slows root uptake. Protect nursery beds with covers.", "warn"))
    else:
        items.append(("Favorable Temperature", "Within optimal physiological range for healthy chlorophyll synthesis.", "ok"))

    if water == "Low":
        items.append(("Water Deficit", "Prioritize micro-drip systems and drought-resilient crops like Guava or Marigold.", "bad"))
    elif water == "Moderate":
        items.append(("Moderate Irrigation", "Sufficient with regular mulching to preserve soil moisture.", "warn"))
    else:
        items.append(("Adequate Water Supply", "Ensure proper furrows and drainage slopes to prevent root rot wilt.", "ok"))
    return items


def diagnose(crop: str, picked: set):
    results = []
    for d in DISEASES:
        if crop not in d["crops"]:
            continue
        overlap = picked & d["symptoms"]
        if overlap:
            results.append((len(overlap) / len(d["symptoms"]), d, overlap))
    results.sort(key=lambda r: r[0], reverse=True)
    return results


# ----------------------------------------------------------------------
# Page Modules
# ----------------------------------------------------------------------
def page_home():
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #09452E 0%, #176B46 50%, #299E66 100%); border-radius: 18px; padding: 2.2rem 2.4rem; color: #FFFFFF; margin-bottom: 1.8rem; box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.2); border: 1px solid rgba(255, 255, 255, 0.12);">
            <span style="display:inline-block; background:rgba(255,255,255,0.18); backdrop-filter:blur(8px); padding:0.3rem 0.8rem; border-radius:30px; font-size:0.85rem; font-weight:600; border:1px solid rgba(255,255,255,0.25);">🌱 Community Service Project • Academic Outreach</span>
            <div style="font-size:2.2rem; font-weight:800; letter-spacing:-0.02em; margin-top:0.6rem; color:#FFFFFF;">Smart Horticulture Advisor</div>
            <div style="font-size:1.05rem; color:#A7F3D0; font-weight:500; margin-bottom:0.8rem;">Sri Venkateswara College of Engineering and Technology (SVCET) • Dept. of Information Technology</div>
            <div style="font-size: 0.95rem; opacity: 0.92; line-height: 1.5; max-width: 850px;">
                Empowering smallholder farmers, women growers, and local communities with data-driven crop suitability insights, pest/disease identification, soil-water diagnostics, transparent market trends, and safe post-harvest washing procedures.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-num">{int(SURVEY_PROBLEMS.iloc[0,1])}%</div>
                <div class="stat-desc">Faced Pest & Disease Loss</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-num">{len(CROPS)}</div>
                <div class="stat-desc">Horticulture Crops Covered</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-num">85%</div>
                <div class="stat-desc">Community Hygiene Uplift</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-num">100%</div>
                <div class="stat-desc">Free Public Domain Advice</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="warn-notice">
            ⚠️ <b>Field Advisory Notice:</b> Recommendations are rule-based expert heuristics designed for academic demonstration and grassroot community assistance. For commercial outbreaks or certified laboratory testing, consult your local district Krishi Vigyan Kendra (KVK) or Agriculture Officer.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🧭 Guided Navigation Modules")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="custom-card">
                <h4 style="color:#34D399; margin-top:0;">🌾 Crop & Disease Advisor</h4>
                <p style="font-size:0.88rem; color:#CBD5E1;">Evaluate your farm's temperature, pH & nitrogen to get scored crop fits or diagnose visible symptoms in real time.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            """
            <div class="custom-card">
                <h4 style="color:#34D399; margin-top:0;">💧 Soil & Water Health</h4>
                <p style="font-size:0.88rem; color:#CBD5E1;">Interactive soil pH gauge and comprehensive field checklist to prevent crop stress and salinity damages.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            """
            <div class="custom-card">
                <h4 style="color:#34D399; margin-top:0;">📈 Market & Hygiene Tools</h4>
                <p style="font-size:0.88rem; color:#CBD5E1;">Track local 30-day mandi commodity price fluctuations and master safe produce washing steps.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def page_survey():
    st.title("📊 Community Field Survey Insights")
    st.caption("Empirical baseline data compiled from field interviews with regional growers and consumers.")

    col_left, col_right = st.columns([1.1, 0.9])
    with col_left:
        fig = px.bar(
            SURVEY_PROBLEMS.sort_values("Respondents (%)"),
            x="Respondents (%)",
            y="Problem",
            orientation="h",
            text="Respondents (%)",
            color="Respondents (%)",
            color_continuous_scale=["#6EE7B7", "#10B981", "#047857"],
            title="Primary Constraints Expressed by Growers (%)"
        )
        fig.update_traces(texttemplate="<b>%{text}%</b>", textposition="outside")
        fig.update_layout(height=360, margin=dict(l=0, r=30, t=40, b=0), xaxis_range=[0, 100], coloraxis_showscale=False)
        show(fig)

    with col_right:
        fig2 = px.pie(
            RESPONDENTS,
            names="Group",
            values="Share",
            hole=0.55,
            color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6"],
            title="Respondent Demographics Breakdown"
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(height=360, margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
        show(fig2)

    st.subheader("Impact Assessment: Knowledge Gain (Before vs After Training)")
    fig3 = px.bar(
        BEFORE_AFTER,
        x="Skill",
        y="Participants (%)",
        color="Stage",
        barmode="group",
        text="Participants (%)",
        color_discrete_map={"Pre-Workshop": "#64748B", "Post-Workshop": "#10B981"},
    )
    fig3.update_traces(texttemplate="<b>%{text}%</b>", textposition="outside")
    fig3.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title=None,
        legend=dict(orientation="h", y=-0.2, x=0.3),
        yaxis_range=[0, 100]
    )
    show(fig3)

    with st.expander("🔬 View Field Trial Observations & Community Feedback"):
        st.markdown(
            """
            - **Vigorous Friction Washing**: Mechanical scrubbing under running water removed over 70% of noticeable surface particulate and dust residues.
            - **Salt & Dilute Vinegar Soak**: A mild 5-minute pre-rinse bath showed helpful degradation of surface contaminants without altering vegetable crispness.
            - **Peeling Trade-offs**: While peeling effectively removes surface residue, it also removes valuable insoluble fiber and vitamins found in fruit skins.
            """
        )


def page_advisor():
    st.title("🌾 Crop & Disease Advisor")
    tab1, tab2 = st.tabs(["🌱 Crop Fit Recommendation", "🔍 Pest & Disease Identifier"])

    with tab1:
        st.write("Provide your field's environmental parameters to calculate matching crop suitability.")
        
        c1, c2 = st.columns(2)
        with c1:
            ph = st.slider("Soil pH Level", 4.0, 9.0, 6.5, 0.1, help="Neutral is ~6.5 - 7.0")
            nitrogen = st.select_slider("Soil Nitrogen Level (N)", options=["Low", "Medium", "High"], value="Medium")
        with c2:
            temp = st.number_input("Average Field Temperature (°C)", min_value=5.0, max_value=45.0, value=26.0, step=0.5)
            water = st.radio("Irrigation Water Availability", ["Low", "Moderate", "Plenty"], index=1, horizontal=True)

        crop_pick = st.selectbox("Detailed Analysis for Specific Crop (Optional)", ["Show All Crops Ranked"] + list(CROPS))

        if st.button("🚀 Calculate Crop Suitability", key="rec"):
            scores = {c: score_crop(c, ph, temp, nitrogen, water) for c in CROPS}
            df = pd.DataFrame({
                "Crop": list(scores),
                "Fit Score": [v[0] for v in scores.values()]
            }).sort_values("Fit Score", ascending=False)

            fig = px.bar(
                df,
                x="Fit Score",
                y="Crop",
                orientation="h",
                text="Fit Score",
                color="Fit Score",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                range_color=[0, 100],
                title="Horticulture Suitability Index (0 - 100)"
            )
            fig.update_traces(texttemplate="<b>%{text} / 100</b>", textposition="outside")
            fig.update_layout(height=400, margin=dict(l=0, r=40, t=40, b=0), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            show(fig)

            best = df.iloc[0]
            st.markdown(
                f"""
                <div class="custom-card" style="border-left: 5px solid {EMERALD};">
                    <span style="font-size:1.15rem; font-weight:700; color:#34D399;">
                        🏆 Highest Recommended Crop: {best['Crop']} (Suitability Score: {int(best['Fit Score'])}/100)
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            focus = best["Crop"] if crop_pick == "Show All Crops Ranked" else crop_pick
            s, notes = score_crop(focus, ph, temp, nitrogen, water)
            
            st.markdown(f"### 📋 Agronomy Checklist for **{focus}** ({s}/100)")
            for n in notes:
                st.markdown(f"- {n}")
            st.markdown(
                f"""
                <div class="info-notice">
                    <b>Resource Benchmarks for {focus}:</b> Recommended Nitrogen: <b>{CROPS[focus]['n']}</b> | Water Requirement: <b>{CROPS[focus]['water']}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

    with tab2:
        st.write("Diagnose crop health problems by selecting observed visual symptoms.")
        col_crop, col_sym = st.columns([1, 2])
        with col_crop:
            crop = st.selectbox("Select Affected Crop", list(CROPS), key="dz_crop")
        with col_sym:
            picked = st.multiselect("Select Observed Symptoms", ALL_SYMPTOMS)

        if st.button("🔍 Diagnose Symptoms", key="dz"):
            if not picked:
                st.warning("Please choose at least one symptom from the list.")
            else:
                found = diagnose(crop, set(picked))
                if not found:
                    st.markdown(
                        """
                        <div class="info-notice">
                            ℹ️ No direct match found in the current symptom database for this specific crop. We suggest capturing high-resolution photos of leaf tops/undersides and contacting the regional extension officer.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"#### Identified Potential Causes ({len(found)} candidate match{'es' if len(found)>1 else ''})")
                    for match, d, overlap in found[:3]:
                        confidence = int(match * 100)
                        badge_color = "#10B981" if confidence >= 70 else "#F59E0B"
                        st.markdown(
                            f"""
                            <div class="custom-card">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <h4 style="margin:0; color:#34D399;">{d['cause']}</h4>
                                    <span style="background:{badge_color}; color:white; font-size:0.8rem; font-weight:700; padding:2px 10px; border-radius:12px;">
                                        {confidence}% Match
                                    </span>
                                </div>
                                <div style="font-size:0.85rem; color:#94A3B8; margin: 6px 0;">
                                    <b>Matching Symptoms:</b> {', '.join(sorted(overlap))}
                                </div>
                                <div style="font-size:0.92rem; color:#CBD5E1; margin-top:8px;">
                                    <b>Recommended Action:</b> {d['advice']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.caption("⚠️ Always adhere strictly to registered pesticide label guidelines, personal protective equipment (PPE), and pre-harvest intervals (PHI).")


def page_soil():
    st.title("💧 Soil & Water Health Evaluation")
    st.caption("Quick field test interpretor based on agronomic standards.")

    col1, col2 = st.columns([1, 1])
    with col1:
        ph = st.slider("Soil pH (Measured)", 4.0, 9.0, 6.5, 0.1, key="s_ph")
        nitrogen = st.select_slider("Soil Nitrogen Fertility", options=["Low", "Medium", "High"], value="Medium", key="s_n")
    with col2:
        temp = st.number_input("Ambient Field Temperature (°C)", 5.0, 45.0, 28.0, 0.5, key="s_t")
        water = st.radio("Irrigation Availability Status", ["Low", "Moderate", "Plenty"], index=1, horizontal=True, key="s_w")

    if st.button("🧪 Generate Field Diagnostic Report", key="soil"):
        col_rpt, col_gauge = st.columns([1.2, 0.8])
        
        with col_rpt:
            st.subheader("Field Status Summary")
            for title, tip, level in soil_water_report(ph, nitrogen, temp, water):
                if level == "ok":
                    st.markdown(
                        f"""
                        <div class="custom-card" style="border-left: 4px solid #10B981; padding: 0.8rem 1rem;">
                            <b>✅ {title}</b><br><span style="color:#CBD5E1; font-size:0.9rem;">{tip}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif level == "warn":
                    st.markdown(
                        f"""
                        <div class="custom-card" style="border-left: 4px solid #F59E0B; padding: 0.8rem 1rem;">
                            <b>⚠️ {title}</b><br><span style="color:#CBD5E1; font-size:0.9rem;">{tip}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="custom-card" style="border-left: 4px solid #EF4444; padding: 0.8rem 1rem;">
                            <b>❌ {title}</b><br><span style="color:#CBD5E1; font-size:0.9rem;">{tip}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        with col_gauge:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ph,
                title={"text": "Soil pH Gauge", "font": {"size": 18, "family": "Plus Jakarta Sans", "color": "#F8FAFC"}},
                gauge={
                    "axis": {"range": [4, 9], "tickwidth": 1, "tickcolor": "#E2E8F0"},
                    "bar": {"color": "#34D399", "thickness": 0.28},
                    "steps": [
                        {"range": [4, 5.5], "color": "#7F1D1D"},
                        {"range": [5.5, 6.0], "color": "#78350F"},
                        {"range": [6.0, 7.5], "color": "#065F46"},
                        {"range": [7.5, 8.0], "color": "#78350F"},
                        {"range": [8.0, 9.0], "color": "#7F1D1D"},
                    ],
                },
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=10))
            show(fig)
            st.caption("<center style='color:#94A3B8;'>Green zone indicates optimal soil nutrient solubility.</center>", unsafe_allow_html=True)


def page_market():
    st.title("📈 Horticulture Market Price Tracker")
    st.caption("Empowering growers with pricing transparency to negotiate better farm-gate realizations.")

    with st.expander("📁 Optional: Upload Real Mandi CSV Data"):
        st.write("Upload a custom CSV file with columns: `Date`, `Crop`, `Price (Rs/kg)`.")
        up = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    
    data = PRICE_DATA
    if up is not None:
        try:
            df = pd.read_csv(up, parse_dates=["Date"])
            if {"Date", "Crop", "Price (Rs/kg)"} <= set(df.columns):
                data = df
                st.success("Successfully loaded custom mandi pricing dataset.")
            else:
                st.error("Uploaded CSV must have headers: Date, Crop, Price (Rs/kg). Displaying baseline data.")
        except Exception as exc:
            st.error(f"Error reading file: {exc}. Displaying default data.")

    crops = sorted(data["Crop"].unique())
    selected_crops = st.multiselect("Select Crops to Compare", crops, default=crops[:4])
    
    if not selected_crops:
        st.info("Select at least one crop to analyze trends.")
        return

    view = data[data["Crop"].isin(selected_crops)]
    fig = px.line(
        view,
        x="Date",
        y="Price (Rs/kg)",
        color="Crop",
        markers=True,
        color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#14B8A6"],
        title="30-Day Wholesale Price Trajectory (₹ per kg)"
    )
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0), legend=dict(orientation="h", y=-0.25))
    show(fig)

    st.subheader("💡 Best Selling Windows & Average Benchmarks")
    cols = st.columns(min(len(selected_crops), 3))
    for i, crop in enumerate(selected_crops):
        sub = view[view["Crop"] == crop].copy()
        sub["Weekday"] = pd.to_datetime(sub["Date"]).dt.day_name()
        by_day = sub.groupby("Weekday")["Price (Rs/kg)"].mean().sort_values(ascending=False)
        latest = sub.sort_values("Date")["Price (Rs/kg)"].iloc[-1]
        avg = sub["Price (Rs/kg)"].mean()
        trend_color = "#34D399" if latest >= avg else "#EF4444"
        trend_icon = "▲" if latest >= avg else "▼"

        with cols[i % len(cols)]:
            st.markdown(
                f"""
                <div class="custom-card">
                    <h4 style="margin:0; color:#34D399;">{crop}</h4>
                    <div style="font-size:1.4rem; font-weight:700; color:{trend_color}; margin: 4px 0;">
                        ₹{latest:.1f} <span style="font-size:0.9rem; font-weight:500;">/ kg</span>
                        <span style="font-size:0.8rem;">({trend_icon} avg ₹{avg:.1f})</span>
                    </div>
                    <div style="font-size:0.85rem; color:#94A3B8;">
                        Peak Mandi Day: <b style="color:#6EE7B7;">{by_day.index[0]}</b> (₹{by_day.iloc[0]:.1f})
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.download_button(
        label="📥 Download Displayed Pricing Data (CSV)",
        data=view.to_csv(index=False).encode(),
        file_name="horticulture_mandi_prices.csv",
        mime="text/csv"
    )


def page_wash():
    st.title("🧼 Safe Produce Washing & Hygiene Guide")
    st.caption("Standardized post-harvest produce cleaning procedures derived from student community trials.")

    item = st.selectbox("Select Horticultural Produce", list(WASH_GUIDE))
    
    st.markdown(f"### Recommended Washing Steps for **{item}**")
    for i, step in enumerate(WASH_GUIDE[item], 1):
        st.markdown(
            f"""
            <div class="custom-card" style="display:flex; align-items:flex-start; gap:12px;">
                <span style="background:#10B981; color:white; border-radius:50%; width:28px; height:28px; display:inline-flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0;">
                    {i}
                </span>
                <span style="font-size:0.95rem; color:#E2E8F0; line-height:1.5;">{step}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="info-notice">
            💡 <b>Key Finding from Community Trials:</b> Vigorous physical rubbing under running clean tap water remains the single most effective household technique, eliminating greater than 70% of external dirt and non-systemic residues.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("✅ Community Safety Action Checklist")
    checklist_items = [
        "Rinse and gently brush all fresh produce before slicing or peeling.",
        "Store perishable greens in ventilated containers away from raw chemicals.",
        "Educate fellow household members and neighbors on washing produce prior to consumption.",
        "Check harvest withholding periods when purchasing directly from local farm gates.",
    ]
    for chk in checklist_items:
        st.checkbox(chk, key=chk)


# ----------------------------------------------------------------------
# Sidebar & Routing
# ----------------------------------------------------------------------
PAGES = {
    "🏠 Home & Overview": page_home,
    "📊 Survey Insights": page_survey,
    "🌾 Crop & Disease Advisor": page_advisor,
    "💧 Soil & Water Health": page_soil,
    "📈 Market Price Tracker": page_market,
    "🧼 Safe Washing Guide": page_wash,
}

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-title">🌱 AgroAdvisor</div>
            <div class="brand-sub">Horticulture Community Service Project</div>
            <span class="brand-tag">SVCET • Dept. of IT</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    choice = st.radio("Navigation", list(PAGES), label_visibility="collapsed")
    st.divider()
    st.caption("Developed by IT Students for Grassroots Agricultural Outreach • 2026")

PAGES[choice]()