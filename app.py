import os
import time
import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from streamlit_js_eval import get_geolocation
import plotly.graph_objects as go
import pytz

# ============================================================
# AIRSEVA AGENT SECTION — ADDED
# ============================================================
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator import run_airseva
# ============================================================


# ================================================================
#  PAGE CONFIG — must be the very first Streamlit call
# ================================================================
st.set_page_config(
    page_title="Air Quality Health Risk Predictor",
    page_icon="🌫",
    layout="wide",
)

load_dotenv()

st.markdown("""
<style>

/* ══ BACKGROUND ══ */
.stApp {
    background: linear-gradient(135deg, #e8f4fd 0%, #d1eaf8 50%, #bee3f8 100%);
    background-attachment: fixed;
}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {
    background-color: #1a3a5c;
}
[data-testid="stSidebar"] *  {
    color: #ffffff !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stMarkdown span {
    color: #ffffff !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #ffffff !important;
    font-weight: 900 !important;
}
[data-testid="stSidebar"] button {
    background-color: #ffffff !important;
    color: #1a3a5c !important;
    border: 1px solid #90caf9 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"],
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #ffffff !important;
}

/* ══ ALL TEXT IN MAIN AREA ══ */
.stApp p, .stApp li, .stApp span,
.stApp label, .stApp div,
.stMarkdown p, .stMarkdown li {
    color: #2c5282 !important;
    font-weight: 600 !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #2c5282 !important;
    font-weight: 700 !important;
}

/* ══ ALL BUTTONS ══ */
.stButton > button,
button {
    background-color: #ffffff !important;
    color: #2c5282 !important;
    border: 1.5px solid #63b3ed !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
.stButton > button:hover {
    background-color: #bee3f8 !important;
    color: #2c5282 !important;
}

/* Form submit / predict button */
[data-testid="stFormSubmitButton"] > button {
    background-color: #63b3ed !important;
    color: #ffffff !important;
    border: 1px solid #63b3ed !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #4299e1 !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background-color: #ffffff !important;
    color: #2c5282 !important;
    border: 1.5px solid #63b3ed !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
[data-testid="stDownloadButton"] button:hover {
    background-color: #bee3f8 !important;
}

/* ══ CHECKBOXES — fully light ══ */
[data-testid="stCheckbox"] {
    background-color: transparent !important;
}
[data-testid="stCheckbox"] label {
    color: #2c5282 !important;
    font-weight: 700 !important;
}
[data-testid="stCheckbox"] span {
    color: #2c5282 !important;
    font-weight: 700 !important;
}
input[type="checkbox"] {
    accent-color: #63b3ed !important;
    width: 16px !important;
    height: 16px !important;
}

/* ══ SLIDER ══ */
[data-testid="stSlider"] p,
[data-testid="stSlider"] span,
[data-testid="stSlider"] label {
    color: #2c5282 !important;
    font-weight: 700 !important;
}
[data-testid="stSlider"] div[role="slider"] {
    background-color: #4299e1 !important;
}

/* ══ FORM ══ */
[data-testid="stForm"] {
    background-color: rgba(255,255,255,0.75) !important;
    border: 1.5px solid #90caf9 !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* ══ INPUT FIELDS ══ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #1a3a5c !important;
    border: 1.5px solid #4299e1 !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}
/* FIX 3: placeholder text now clearly visible */
[data-testid="stTextInput"] input::placeholder {
    color: #7bafd4 !important;
    font-weight: 500 !important;
    opacity: 1 !important;
}

/* ══ METRICS ══ */
[data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #2c5282 !important;
}
[data-testid="stMetricLabel"] {
    color: #2c5282 !important;
    font-weight: 700 !important;
}
[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.80) !important;
    border-radius: 10px !important;
    padding: 8px !important;
    border: 1px solid #90caf9 !important;
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(255,255,255,0.70) !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 700 !important;
    color: #2c5282 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #63b3ed !important;
    color: #ffffff !important;
    border-radius: 6px !important;
}

/* ══ CHARTS — do not override plotly ══ */
.js-plotly-plot {
    border-radius: 10px;
    overflow: hidden;
}

/* ══ ALERT / INFO BOXES ══ */
[data-testid="stAlert"] {
    background-color: #ebf8ff !important;
    color: #2c5282 !important;
    border-radius: 8px !important;
    border: 1px solid #90caf9 !important;
}
[data-testid="stAlert"] p {
    color: #2c5282 !important;
}

/* ══ EXPANDER ══ */
[data-testid="stExpander"] {
    background-color: rgba(255,255,255,0.80) !important;
    border: 1px solid #90caf9 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #2c5282 !important;
    font-weight: 700 !important;
}

/* ══ PROGRESS BAR ══ */
[data-testid="stProgress"] > div > div {
    background-color: #4299e1 !important;
}
[data-testid="stProgress"] {
    background-color: #bee3f8 !important;
}

/* ══ CAPTION ══ */
[data-testid="stCaptionContainer"] p {
    color: #2c5282 !important;
    font-weight: 600 !important;
}

/* ══ DATAFRAME ══ */
[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.90) !important;
    border-radius: 8px !important;
    border: 1px solid #90caf9 !important;
}

/* ══ NUMBER INPUT +/- BUTTONS ══ */
[data-testid="stNumberInput"] button {
    background-color: #e8f4fd !important;
    color: #2c5282 !important;
    border: 1px solid #90caf9 !important;
}

/* ══ DIVIDER ══ */
hr {
    border-color: #90caf9 !important;
    opacity: 0.5 !important;
}

/* ══ SPINNER ══ */
[data-testid="stSpinner"] p {
    color: #2c5282 !important;
    font-weight: 700 !important;
}

/* ══ SUCCESS / INFO / WARNING ══ */
.stSuccess, .stInfo, .stWarning, .stError {
    color: #2c5282 !important;
}

</style>
""", unsafe_allow_html=True)


# ================================================================
#  HELPERS
# ================================================================
def aqi_category(aqi):
    try:
        aqi = int(aqi)
    except (TypeError, ValueError):
        return "Unknown", "⚪", "#aaaaaa"
    if aqi <= 50:    return "Good",                           "🟢", "#00e400"
    elif aqi <= 100: return "Moderate",                       "🟡", "#ffff00"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups", "🟠", "#ff7e00"
    elif aqi <= 200: return "Unhealthy",                      "🔴", "#ff0000"
    elif aqi <= 300: return "Very Unhealthy",                 "🟣", "#8f3f97"
    else:            return "Hazardous",                      "⚫", "#7e0023"


# ============================================================
# AIRSEVA AGENT SECTION
# ============================================================

# 1. HEADER
st.title("🌬️ AirSeva — Agentic Air Quality Health Advisory")
st.markdown("### Powered by Multi-Agent AI | WAQI + Gemini 2.5 Flash + Random Forest")

# City coordinate lookup for supported cities
CITY_COORDS = {
    "Ahmedabad": (23.0225, 72.5714),
    "Aizawl": (23.7271, 92.7176),
    "Amaravati": (16.5730, 80.3582),
    "Amritsar": (31.6340, 74.8723),
    "Bengaluru": (12.9716, 77.5946),
    "Bhopal": (23.2599, 77.4126),
    "Brajrajnagar": (21.8167, 83.9167),
    "Chandigarh": (30.7333, 76.7794),
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Delhi": (28.7041, 77.1025),
    "Ernakulam": (9.9816, 76.2999),
    "Gurugram": (28.4595, 77.0266),
    "Guwahati": (26.1445, 91.7362),
    "Hyderabad": (17.3850, 78.4867),
    "Jaipur": (26.9124, 75.7873),
    "Jorapokhar": (23.6800, 86.4200),
    "Kochi": (9.9312, 76.2673),
    "Kolkata": (22.5726, 88.3639),
    "Lucknow": (26.8467, 80.9462),
    "Mumbai": (19.0760, 72.8777),
    "Patna": (25.5941, 85.1376),
    "Shillong": (25.5788, 91.8933),
    "Talcher": (20.9500, 85.2333),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Visakhapatnam": (17.6868, 83.2185)
}

def find_nearest_supported_city(lat, lon):
    import math
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
    
    nearest = min(CITY_COORDS.keys(), 
                  key=lambda c: haversine(lat, lon, 
                                          CITY_COORDS[c][0], 
                                          CITY_COORDS[c][1]))
    return nearest

# Initialize state keys
if "airseva_gps_waiting" not in st.session_state:
    st.session_state["airseva_gps_waiting"] = False
if "airseva_gps_just_detected" not in st.session_state:
    st.session_state["airseva_gps_just_detected"] = False
if "airseva_detected_city" not in st.session_state:
    st.session_state["airseva_detected_city"] = None
if "airseva_detected_lat" not in st.session_state:
    st.session_state["airseva_detected_lat"] = None
if "airseva_detected_lon" not in st.session_state:
    st.session_state["airseva_detected_lon"] = None
if "airseva_city_input" not in st.session_state:
    st.session_state["airseva_city_input"] = "Bengaluru"
if "airseva_age" not in st.session_state:
    st.session_state["airseva_age"] = 25
if "airseva_asthma" not in st.session_state:
    st.session_state["airseva_asthma"] = False
if "airseva_smoker" not in st.session_state:
    st.session_state["airseva_smoker"] = False
if "airseva_outdoor_worker" not in st.session_state:
    st.session_state["airseva_outdoor_worker"] = False

# Layout: two columns
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📍 Enter Location")

    if st.button("📍 Detect My Location (GPS)", use_container_width=True, key="airseva_gps_btn"):
        st.session_state.airseva_gps_waiting = True
        st.rerun()

    if st.session_state.airseva_gps_waiting:
        with st.spinner("📡 Waiting for browser GPS... allow location if prompted."):
            loc = get_geolocation()
        if loc and "coords" in loc:
            lat      = loc["coords"]["latitude"]
            lon      = loc["coords"]["longitude"]
            
            # Resolve nearest supported city
            nearest_city = find_nearest_supported_city(lat, lon)
            
            st.session_state.airseva_detected_lat      = lat
            st.session_state.airseva_detected_lon      = lon
            st.session_state.airseva_detected_city     = nearest_city
            st.session_state.airseva_gps_waiting       = False
            st.session_state.airseva_gps_just_detected = True
            
            st.success(f"📍 Detected coordinates: {lat:.4f}, {lon:.4f}")
            st.info(f"📍 GPS detected your location. Nearest supported city: **{nearest_city}**")
        else:
            st.info("⏳ Requesting GPS from browser... please wait.")
            time.sleep(1)
            st.rerun()

    # Only sync GPS city right after detection — not on every rerun
    if st.session_state.get("airseva_gps_just_detected"):
        st.session_state["airseva_city_input"] = st.session_state.airseva_detected_city or "Bengaluru"
        st.session_state["airseva_gps_just_detected"] = False

    # Get current typed/detected city value from state
    current_city_val = st.session_state.get("airseva_city_input", "Bengaluru").strip()

    # Check if current_city_val is supported
    SUPPORTED_CITIES = [
        "Ahmedabad",
        "Aizawl", 
        "Amaravati",
        "Amritsar",
        "Bengaluru",
        "Bhopal",
        "Brajrajnagar",
        "Chandigarh",
        "Chennai",
        "Coimbatore",
        "Delhi",
        "Ernakulam",
        "Gurugram",
        "Guwahati",
        "Hyderabad",
        "Jaipur",
        "Jorapokhar",
        "Kochi",
        "Kolkata",
        "Lucknow",
        "Mumbai",
        "Patna",
        "Shillong",
        "Talcher",
        "Thiruvananthapuram",
        "Visakhapatnam"
    ]
    supported_lower = [c.lower() for c in SUPPORTED_CITIES]
    is_supported = current_city_val.lower() in supported_lower

    if is_supported:
        city_val = st.text_input(
            "🏙️ City / Town / Village",
            placeholder="e.g. Bangalore, Anekal, Mysore, Hubli",
            help="Type any city, town, or village — or use GPS above.",
            key="airseva_city_input",
        )
        city_to_run = city_val.strip()
    else:
        st.warning(f"'{current_city_val}' is not in our supported list. Showing results for nearest city. Please select from the dropdown instead.")
        
        selected_fallback = st.selectbox(
            "🏙️ City / Town / Village (Supported Fallback)",
            options=SUPPORTED_CITIES,
            index=SUPPORTED_CITIES.index("Bengaluru"),
            key="airseva_city_input_fallback"
        )
        st.session_state["airseva_city_input"] = selected_fallback
        city_to_run = selected_fallback

    st.markdown("### 🧍 Personal Health Profile")
    st.caption("Your profile personalises the health risk advice.")

    airseva_age = st.slider(
        "Age", 5, 80,
        value=st.session_state["airseva_age"],
        key="airseva_age_slider",
        help="Children <12 and adults >60 are at higher pollution risk.",
    )

    airseva_asthma = st.checkbox("🫁 Asthma", value=st.session_state["airseva_asthma"], key="airseva_asthma_cb")
    airseva_smoker = st.checkbox("🚬 Smoker", value=st.session_state["airseva_smoker"], key="airseva_smoker_cb")
    airseva_outdoor_worker = st.checkbox("👷 Outdoor Worker", value=st.session_state["airseva_outdoor_worker"], key="airseva_outdoor_cb")

    # Auto-calculated score
    vulnerability_score = 0
    if airseva_age < 12 or airseva_age > 60:
        vulnerability_score += 2
    if airseva_asthma:
        vulnerability_score += 3
    if airseva_smoker:
        vulnerability_score += 2
    if airseva_outdoor_worker:
        vulnerability_score += 1

    if vulnerability_score <= 1:
        vuln_label = "🟢 Low"
    elif vulnerability_score <= 4:
        vuln_label = "🟡 Moderate"
    else:
        vuln_label = "🔴 High"

    st.markdown(
        f"**Personal Vulnerability:** {vuln_label} &nbsp;`score: {vulnerability_score}/8`",
        unsafe_allow_html=True,
    )

    # Update session states
    st.session_state["airseva_age"] = airseva_age
    st.session_state["airseva_asthma"] = airseva_asthma
    st.session_state["airseva_smoker"] = airseva_smoker
    st.session_state["airseva_outdoor_worker"] = airseva_outdoor_worker

    # 3. RUN BUTTON
    if st.button("🚀 Run AirSeva Analysis", use_container_width=True, key="airseva_run_btn"):
        if not city_to_run:
            st.error("⚠️ Please enter a city, town, or village name before running analysis.")
        else:
            with st.spinner("⏳ Running multi-agent analysis... 15–30 seconds"):
                try:
                    # Call orchestrator
                    result = run_airseva(city_to_run, vulnerability_score)
                    # Store result
                    st.session_state["airseva_result"] = result
                except Exception as e:
                    # Python exception handling
                    st.error("⚠️ Unexpected error. Please try again.")
                    import traceback
                    traceback.print_exc()

with right_col:
    # Keep empty for now (results will go here later)
    pass

# 4. RESULTS DISPLAY
if "airseva_result" not in st.session_state:
    st.session_state["airseva_result"] = None

if st.session_state["airseva_result"] is not None:
    result = st.session_state["airseva_result"]
    # Check if result dictionary contains an error (for error handling requirement 5)
    if isinstance(result, dict) and result.get("error") is not None:
        st.error(f"⚠️ Analysis failed: {result['error']}")
        st.info("💡 Check WAQI_TOKEN and GEMINI_API_KEY in .env")
    else:
        # Map who_warnings, probabilities and adjust confidence to fraction
        if "who_warnings" not in result:
            who_exceedances = result.get("who_exceedances", {})
            who_limits = result.get("who_limits", {})
            pollutants = result.get("pollutants", {})
            warnings_list = []
            for pollutant, exceeded in who_exceedances.items():
                if exceeded:
                    val = pollutants.get(pollutant, 0)
                    unit = "mg/m³" if pollutant == 'co' else "µg/m³"
                    limit_key = f"{pollutant}_24h"
                    if limit_key not in who_limits:
                        limit_key = f"{pollutant}_annual"
                    if limit_key not in who_limits:
                        limit_key = f"{pollutant}_8h"
                    limit = who_limits.get(limit_key, 0)
                    warnings_list.append(f"WARNING: {pollutant.upper()} concentration ({val} {unit}) exceeds WHO limit of {limit} {unit}")
            result["who_warnings"] = warnings_list

        if "probabilities" not in result:
            result["probabilities"] = result.get("model_probabilities", {})

        # Ensure confidence is a fraction for the template's formula
        conf_raw = result.get("confidence", 0.0)
        if conf_raw > 1.0:
            result["confidence"] = conf_raw / 100.0

        # Formatted IST timestamp helper function
        def format_timestamp(ts_str):
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(ts_str)
                ist = pytz.timezone('Asia/Kolkata')
                if dt.tzinfo is None:
                    dt = ist.localize(dt)
                else:
                    dt = dt.astimezone(ist)
                return dt.strftime("%B %d, %Y at %I:%M %p IST")
            except:
                return ts_str

        # IMPROVEMENT 4: AGENT PIPELINE STATUS BANNER
        st.markdown("### ✅ Agent Pipeline — All Steps Complete")
        col1, col2, col3, col4 = st.columns(4)
        col1.success("✅ Agent 1\nData Fetched")
        col2.success("✅ Agent 2\nRisk Predicted")
        col3.success("✅ Agent 3\nAdvisory Generated")
        col4.success("✅ Agent 4\nReport Compiled")
        st.divider()

        # A. AQI SUMMARY
        st.subheader("📋 Air Quality & Risk Summary")
        sum_col1, sum_col2, sum_col3 = st.columns(3)
        
        with sum_col1:
            st.metric("AQI Value", result.get("aqi_value", 0))
            
        with sum_col2:
            risk_lvl = result.get("risk_level", "Low")
            if risk_lvl == "High":
                st.error("🔴 Risk Level: High")
            elif risk_lvl == "Moderate":
                st.warning("🟠 Risk Level: Moderate")
            else:
                st.success("🟢 Risk Level: Low")
                
        with sum_col3:
            # Handle fraction vs percentage for confidence
            conf_val = result.get("confidence", 0.0)
            if conf_val <= 1.0:
                conf_val = conf_val * 100
            st.metric("Model Confidence", f"{conf_val:.1f}%")

        # IMPROVEMENT 1: AQI GAUGE CHART
        aqi_val = result.get("aqi_value", 0)
        cat, cat_emoji, cat_color = aqi_category(aqi_val)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi_val,
            title={"text": "Air Quality Index",
                   "font": {"color": "#000000", "size": 18}},
            number={"font": {"color": "#000000", "size": 52}},
            gauge={
                "axis": {
                    "range": [0, 500],
                    "tickcolor": "#000000",
                    "tickfont": {"color": "#000000", "size": 13},
                },
                "bar":  {"color": "#1d4ed8", "thickness": 0.3},
                "bgcolor": "#ffffff",
                "borderwidth": 2,
                "bordercolor": "#94a3b8",
                "steps": [
                    {"range": [0,   50],  "color": "#16a34a"},
                    {"range": [50,  100], "color": "#ca8a04"},
                    {"range": [100, 150], "color": "#ea580c"},
                    {"range": [150, 200], "color": "#dc2626"},
                    {"range": [200, 300], "color": "#7c3aed"},
                    {"range": [300, 500], "color": "#9f1239"},
                ],
                "threshold": {
                    "line": {"color": "#000000", "width": 5},
                    "thickness": 0.8, "value": aqi_val,
                },
            },
        ))
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font={"color": "#000000", "family": "Arial", "size": 14},
            margin={"t": 80, "b": 30, "l": 30, "r": 30},
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

        # B. WHO WARNINGS
        st.markdown("### ⚠️ WHO 2021 Guideline Warnings")
        who_exceedances = result.get("who_exceedances", {})
        who_limits = result.get("who_limits", {})
        pollutants = result.get("pollutants", {})
        
        warnings_list = result.get("who_warnings", [])
        
        if warnings_list:
            for warning in warnings_list:
                st.warning(warning)
        else:
            st.success("✅ All pollutants within WHO 2021 guidelines")

        # C. POLLUTANT TABLE
        st.markdown("### 📊 Pollutant Readings")
        pollutants_dict = result.get("pollutants", {})
        pollutants_data = [{"Pollutant": k.upper(), "Value": v} for k, v in pollutants_dict.items()]
        df_pollutants = pd.DataFrame(pollutants_data)
        st.dataframe(df_pollutants, use_container_width=True)

        # IMPROVEMENT 2: POLLUTANT BAR CHART VS WHO LIMITS
        st.markdown("### 📊 Pollutant vs WHO 2021 Limits")
        pm_data = result.get("pollutants", {})
        pollutant_df = pd.DataFrame({
            "Pollutant": ["PM2.5", "PM10", "CO", "NO2", "O3", "SO2"],
            "Measured":  [
                pm_data.get("pm25", 0.0),
                pm_data.get("pm10", 0.0),
                pm_data.get("co", 0.0),
                pm_data.get("no2", 0.0),
                pm_data.get("o3", 0.0),
                pm_data.get("so2", 0.0)
            ],
            "WHO Limit": [15.0, 45.0, 4.0, 10.0, 60.0, 40.0],
        })
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Measured",
            x=pollutant_df["Pollutant"],
            y=pollutant_df["Measured"],
            marker_color="#1d4ed8",
            marker_line_color="#1e3a8a",
            marker_line_width=1.5,
        ))
        fig2.add_trace(go.Bar(
            name="WHO Safe Limit",
            x=pollutant_df["Pollutant"],
            y=pollutant_df["WHO Limit"],
            marker_color="#b91c1c",
            marker_line_color="#7f1d1d",
            marker_line_width=1.5,
        ))
        fig2.update_layout(
            template="plotly_white",
            barmode="group",
            title={
                "text": "Pollutant Concentration vs WHO Safe Limits (2021)",
                "font": {"color": "#000000", "size": 14},
                "x": 0,
            },
            legend=dict(
                orientation="h",
                font={"color": "#000000", "size": 12},
                bgcolor="#ffffff",
                bordercolor="#94a3b8",
                borderwidth=1,
            ),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font={"color": "#000000", "family": "Arial", "size": 13},
            xaxis={
                "tickfont": {"color": "#000000", "size": 13},
                "title_font": {"color": "#000000"},
                "linecolor": "#000000",
                "gridcolor": "#e2e8f0",
            },
            yaxis={
                "tickfont": {"color": "#000000", "size": 13},
                "title_font": {"color": "#000000"},
                "linecolor": "#000000",
                "gridcolor": "#e2e8f0",
            },
            margin={"t": 60, "b": 50, "l": 50, "r": 20},
        )
        st.plotly_chart(fig2, use_container_width=True)

        # D. MODEL PROBABILITIES
        st.markdown("### 🤖 Model Probabilities")
        probs = result.get("model_probabilities", {})
        prob_col1, prob_col2, prob_col3 = st.columns(3)
        prob_col1.metric("High Risk", f"{probs.get('High', 0.0) * 100:.1f}%")
        prob_col2.metric("Moderate Risk", f"{probs.get('Moderate', 0.0) * 100:.1f}%")
        prob_col3.metric("Low Risk", f"{probs.get('Low', 0.0) * 100:.1f}%")

        # E. GEMINI ADVISORY
        st.markdown("### 💊 Health Advisory (Gemini 2.5 Flash)")
        st.info(result.get("advisory", ""))
        
        # IMPROVEMENT 3: FIX TIMESTAMP FORMAT
        st.caption(f"🕐 Generated at: {format_timestamp(result['timestamp'])}")

        # IMPROVEMENT 5: DOWNLOAD REPORT BUTTON
        st.markdown("### 📥 Download Your Report")
        now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        
        report_text = f"""
AIRSEVA -- AIR QUALITY HEALTH ADVISORY REPORT
Generated at: {format_timestamp(result['timestamp'])}
============================================

CITY: {result['city']}
AQI VALUE: {result['aqi_value']}
RISK LEVEL: {result['risk_level']}
MODEL CONFIDENCE: {result['confidence']*100:.1f}%

WHO 2021 GUIDELINE WARNINGS:
{chr(10).join(result['who_warnings']) if result['who_warnings'] else 'All pollutants within WHO limits'}

POLLUTANT READINGS:
{chr(10).join([f"  {k}: {v}" for k,v in result['pollutants'].items()])}

MODEL PROBABILITIES:
  High Risk: {result['probabilities']['High']*100:.1f}%
  Moderate Risk: {result['probabilities']['Moderate']*100:.1f}%
  Low Risk: {result['probabilities']['Low']*100:.1f}%

HEALTH ADVISORY (Gemini 2.5 Flash):
{result['advisory']}

============================================
Generated by AirSeva -- Agentic Air Quality Health Advisory System
Powered by WAQI + Gemini 2.5 Flash + Random Forest ML
"""

        # Generate PDF using fpdf2
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=10)
        
        # Split and clean report text to fit standard latin-1 encoding of standard PDF fonts
        for line in report_text.split("\n"):
            line_clean = line.replace("—", "-").replace("µg/m³", "ug/m3").replace("mg/m³", "mg/m3").replace("³", "3").replace("`", "'").replace("🕐", "").replace("✅", "").replace("🔴", "").replace("🟠", "").replace("🟢", "").replace("💊", "").replace("📥", "").replace("📊", "").replace("🤖", "").replace("⚠️", "")
            line_clean = line_clean.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 6, text=line_clean, new_x="LMARGIN", new_y="NEXT")
            
        pdf_bytes = bytes(pdf.output())

        st.download_button(
            label="📄 Download Full Report as PDF",
            data=pdf_bytes,
            file_name=f"AirSeva_Report_{result['city']}_{now_str}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ================================================================
#  FOOTER
# ================================================================
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.markdown(
    "<p style='color:#2c5282; font-weight:700; font-size:13px;'>"
    "🌫 Air Quality Health Risk Prediction System</p>",
    unsafe_allow_html=True,
)
c2.markdown(
    "<p style='color:#2c5282; font-weight:700; font-size:13px; text-align:center;'>"
    "🤖 Powered by Random Forest ML + WAQI API</p>",
    unsafe_allow_html=True,
)
c3.markdown(
    "<p style='color:#2c5282; font-weight:700; font-size:13px; text-align:right;'>"
    "👨‍💻 Developed by Shreenivas S B</p>",
    unsafe_allow_html=True,
)