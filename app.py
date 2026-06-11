import os
import time
import datetime
import streamlit as st
import pandas as pd
import joblib
import requests
import numpy as np
from dotenv import load_dotenv
from streamlit_js_eval import get_geolocation
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
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
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "")

# Also support Streamlit Cloud secrets (for deployment)
if not WAQI_TOKEN:
    try:
        WAQI_TOKEN = st.secrets.get("WAQI_TOKEN", "")
    except Exception:
        pass

if not WAQI_TOKEN:
    st.error("❌ WAQI_TOKEN not found. Please create a `.env` file with your API token.")
    st.stop()

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
#  MODEL LOADING  — cached so it loads only ONCE across all sessions
# ================================================================
@st.cache_resource
def load_model():
    base_dir   = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "models", "health_risk_rf_model.pkl")
    if not os.path.exists(model_path):
        model_path = os.path.join(base_dir, "..", "models", "health_risk_rf_model.pkl")
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        st.error(
            "❌ Model file not found. "
            "Ensure `health_risk_rf_model.pkl` is inside the `models/` folder."
        )
        st.stop()

model = load_model()

# ================================================================
#  SESSION STATE  — initialize all keys once
# ================================================================
DEFAULTS = {
    "detected_city":      None,
    "detected_lat":       None,
    "detected_lon":       None,
    "live_data":          None,
    "prediction":         None,
    "confidence":         None,
    "forecast_pred":      None,
    "vuln_score":         0,
    "age":                25,
    "asthma":             False,
    "smoker":             False,
    "outdoor_worker":     False,
    "gps_waiting":        False,
    "gps_just_detected":  False,
    "pm25_history":       [],   # last 7 PM2.5 readings for real lag/rolling features
    "aqi_history":        [],   # for session AQI chart
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


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


def reverse_geocode(lat, lon):
    try:
        res = requests.get(
            f"https://nominatim.openstreetmap.org/reverse"
            f"?lat={lat}&lon={lon}&format=json&zoom=10&addressdetails=1",
            headers={"User-Agent": "air-quality-app"}, timeout=10,
        ).json()
        a = res.get("address", {})
        return (a.get("village") or a.get("town") or a.get("suburb")
                or a.get("city") or a.get("county") or a.get("state"))
    except Exception:
        return None


def geocode_city(city):
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "air-quality-app"}, timeout=8,
        ).json()
        if res:
            return float(res[0]["lat"]), float(res[0]["lon"])
    except Exception:
        pass
    return None, None


def _parse_waqi(res):
    data = res.get("data", {})
    iaqi = data.get("iaqi", {})
    gv   = lambda p: iaqi.get(p, {}).get("v", 0)

    # WAQI sometimes returns "-" for stale AQI — safely cast to int
    raw_aqi = data.get("aqi", 0)
    try:
        aqi_val = int(raw_aqi)
    except (TypeError, ValueError):
        aqi_val = 0

    return {
        "pm25":          gv("pm25"),
        "pm10":          gv("pm10"),
        "co":            gv("co"),
        "no2":           gv("no2"),
        "o3":            gv("o3"),
        "so2":           gv("so2"),   # added for report
        "nh3":           gv("nh3"),   # added for report
        "aqi":           aqi_val,
        "timestamp":     data.get("time", {}).get("s", "N/A"),
        "lat":           data.get("city", {}).get("geo", [0, 0])[0],
        "lon":           data.get("city", {}).get("geo", [0, 0])[1],
        "station":       data.get("city", {}).get("name", ""),
        "forecast_pm25": data.get("forecast", {}).get("daily", {}).get("pm25", []),
    }


@st.cache_data(ttl=600)
def fetch_by_city(city):
    try:
        res = requests.get(
            f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10,
        ).json()
        return _parse_waqi(res) if res.get("status") == "ok" else None
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_by_coords(lat, lon):
    try:
        res = requests.get(
            f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10,
        ).json()
        return _parse_waqi(res) if res.get("status") == "ok" else None
    except Exception:
        return None


def fetch_live_pollution(city=None, lat=None, lon=None):
    """
    3-layer fallback: city name → GPS coords → geocode → nearest station.
    FIX: Returns (data, message) — st.* calls kept out of cached functions.
    """
    fallback_msg = None
    data = fetch_by_city(city) if city else None

    if data is None and lat is not None and lon is not None:
        data = fetch_by_coords(lat, lon)
        if data:
            fallback_msg = (
                f"ℹ️ No direct station for **{city}**. "
                f"Showing nearest: **{data['station']}**"
            )

    if data is None and city:
        geo_lat, geo_lon = geocode_city(city)
        if geo_lat is not None:
            data = fetch_by_coords(geo_lat, geo_lon)
            if data:
                fallback_msg = (
                    f"ℹ️ Auto-located **{city}** → nearest station: **{data['station']}**"
                )
        else:
            fallback_msg = f"⚠️ Could not find **{city}**. Check spelling and try again."

    return data, fallback_msg


def compute_lag_features(current_pm25):
    """Use actual stored PM2.5 history for lag and rolling features."""
    h     = st.session_state.pm25_history
    lag1  = h[-2] if len(h) >= 2 else current_pm25
    lag3  = h[-4] if len(h) >= 4 else current_pm25
    lag7  = h[-7] if len(h) >= 7 else current_pm25
    roll3 = float(np.mean(h[-3:])) if len(h) >= 3 else current_pm25
    roll7 = float(np.mean(h[-7:])) if len(h) >= 7 else current_pm25
    return lag1, lag3, lag7, roll3, roll7


def build_features(pm25, pm10, co, no2, o3):
    """Build feature DataFrame matching EXACTLY the order model was trained on."""
    today = datetime.date.today()
    lag1, lag3, lag7, roll3, roll7 = compute_lag_features(pm25)
    feat = {
        "pm25":         pm25,
        "pm10":         pm10,
        "no":           0,
        "no2":          no2,
        "nox":          0,
        "nh3":          0,
        "co":           co,
        "so2":          0,
        "o3":           o3,
        "benzene":      0,
        "toluene":      0,
        "xylene":       0,
        "city_encoded": 0,
        "pm25_lag_1":   lag1,
        "pm25_lag_3":   lag3,
        "pm25_lag_7":   lag7,
        "pm25_roll_3":  roll3,
        "pm25_roll_7":  roll7,
        "year":         today.year,
        "month":        today.month,
        "day":          today.day,
        "day_of_week":  today.weekday(),
    }
    order = [
        'pm25', 'pm10', 'no', 'no2', 'nox', 'nh3', 'co', 'so2', 'o3',
        'benzene', 'toluene', 'xylene', 'city_encoded',
        'pm25_lag_1', 'pm25_lag_3', 'pm25_lag_7',
        'pm25_roll_3', 'pm25_roll_7',
        'year', 'month', 'day', 'day_of_week'
    ]
    return pd.DataFrame([feat])[order]


def run_prediction(pm25, pm10, co, no2, o3):
    df   = build_features(pm25, pm10, co, no2, o3)
    pred = model.predict(df)[0]
    conf = max(model.predict_proba(df)[0]) * 100
    return pred, conf


def generate_forecast(pm25, pm10, co, no2, o3):
    results   = []
    today     = datetime.date.today()
    scenarios = [
        {"m25": 1.05, "m10": 1.03},
        {"m25": 1.10, "m10": 1.05},
        {"m25": 0.95, "m10": 0.97},
    ]
    order = [
        'pm25', 'pm10', 'no', 'no2', 'nox', 'nh3', 'co', 'so2', 'o3',
        'benzene', 'toluene', 'xylene', 'city_encoded',
        'pm25_lag_1', 'pm25_lag_3', 'pm25_lag_7',
        'pm25_roll_3', 'pm25_roll_7',
        'year', 'month', 'day', 'day_of_week'
    ]
    lag1, lag3, lag7, roll3, roll7 = compute_lag_features(pm25)

    for i, sc in enumerate(scenarios):
        fd   = today + datetime.timedelta(days=i + 1)
        feat = {
            "pm25":         pm25 * sc["m25"],
            "pm10":         pm10 * sc["m10"],
            "no":           0, "no2": no2, "nox": 0, "nh3": 0,
            "co":           co, "so2": 0, "o3": o3,
            "benzene":      0, "toluene": 0, "xylene": 0,
            "city_encoded": 0,
            "pm25_lag_1":   lag1,
            "pm25_lag_3":   lag3,
            "pm25_lag_7":   lag7,
            "pm25_roll_3":  roll3,
            "pm25_roll_7":  roll7,
            "year":         fd.year,
            "month":        fd.month,
            "day":          fd.day,
            "day_of_week":  fd.weekday(),
        }
        df   = pd.DataFrame([feat])[order]
        risk = model.predict(df)[0]
        results.append((fd.strftime("%a, %d %b"), risk))
    return results


# ================================================================
#  SIDEBAR
# ================================================================
with st.sidebar:
    # Brand header
    st.markdown("""
    <div style="background-color:#0d2137; padding:14px 10px; border-radius:8px; margin-bottom:10px;">
        <p style="color:#ffffff !important; font-weight:900 !important; font-size:20px !important;
                  margin:0 !important; text-align:center; letter-spacing:0.5px;">
            AQI Health Prediction
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # FIX 1: "AQI Predictor" — bright white via raw HTML (st.title() gets overridden by sidebar dark theme)
    st.markdown("""
    <div style="padding:4px 0 10px 0;">
        <p style="color:#ffffff !important; font-weight:900 !important;
                  font-size:26px !important; margin:0 !important; letter-spacing:0.5px;">
            🌫 AQI Predictor
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown(
        "**1.** 📍 Click GPS or type a location\n\n"
        "**2.** Fill your health profile\n\n"
        "**3.** Click **Fetch AQI & Predict**"
    )
    st.markdown("---")
    st.markdown("**Risk Levels:**")
    st.markdown("🟢 **Low** — Safe outdoors\n\n🟡 **Moderate** — Limit exertion\n\n🔴 **High** — Stay indoors")
    st.markdown("---")

    if st.session_state.live_data:
        ld = st.session_state.live_data
        cat, emoji, _ = aqi_category(ld["aqi"])

        # FIX: Sidebar station info card — fully white, always visible
        st.markdown(
            f"""<div style="background:#0d2137; border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                <p style="color:#90cdf4 !important; font-size:11px; margin:0 0 4px 0; font-weight:600;">
                    📡 LAST STATION
                </p>
                <p style="color:#ffffff !important; font-size:13px; margin:0 0 6px 0; font-weight:700;">
                    {ld['station']}
                </p>
                <p style="color:#ffffff !important; font-size:14px; margin:0 0 2px 0; font-weight:800;">
                    AQI: {ld['aqi']} {emoji}
                </p>
                <p style="color:#90cdf4 !important; font-size:11px; margin:0; font-weight:600;">
                    🕒 {ld['timestamp']}
                </p>
            </div>""",
            unsafe_allow_html=True,
        )

        # Vulnerability score in sidebar
        vuln = st.session_state.vuln_score
        vuln_label = ("🟢 Low" if vuln <= 1 else "🟡 Moderate" if vuln <= 4 else "🔴 High")
        st.markdown(
            f"<p style='color:#ffffff !important; font-size:13px; font-weight:700;'>"
            f"👤 Vulnerability: {vuln_label} ({vuln}/8)</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        if st.button("🔄 Refresh AQI Data", use_container_width=True):
            fetch_by_city.clear()
            fetch_by_coords.clear()
            st.rerun()

    # PM2.5 session history chart
    if len(st.session_state.pm25_history) > 1:
        st.markdown("**📈 PM2.5 This Session:**")
        st.line_chart(
            pd.DataFrame({"PM2.5": st.session_state.pm25_history}),
            height=120,
        )


# ================================================================
#  HEADER
# ================================================================
st.title("🌫 Air Quality Health Risk Prediction System")
st.success("🔴 Live Location Based Air Quality & Personalised Health Risk Prediction")

tab1, tab2, tab3 = st.tabs(["📍 Location & AQI", "📊 Health Prediction & Advice", "🤖 AirSeva Agent"])


# ================================================================
#  TAB 1 — LOCATION INPUT + AQI DISPLAY
# ================================================================
with tab1:
    left, right = st.columns([1, 1])

    with left:
        st.subheader("📍 Enter Location")

        if st.button("📍 Detect My Location (GPS)", use_container_width=True):
            st.session_state.gps_waiting = True
            st.rerun()

        if st.session_state.gps_waiting:
            with st.spinner("📡 Waiting for browser GPS... allow location if prompted."):
                loc = get_geolocation()
            if loc and "coords" in loc:
                lat      = loc["coords"]["latitude"]
                lon      = loc["coords"]["longitude"]
                city_det = reverse_geocode(lat, lon)
                st.session_state.detected_lat      = lat
                st.session_state.detected_lon      = lon
                st.session_state.detected_city     = city_det or f"{lat:.4f},{lon:.4f}"
                st.session_state.gps_waiting       = False
                st.session_state.gps_just_detected = True
                st.success(f"📍 Detected: **{st.session_state.detected_city}**")
            else:
                st.info("⏳ Requesting GPS from browser... please wait.")
                time.sleep(1)
                st.rerun()

        # Initialize city_input only once
        if "city_input" not in st.session_state:
            st.session_state["city_input"] = st.session_state.detected_city or ""
        # Only sync GPS city right after detection — not on every rerun
        if st.session_state.get("gps_just_detected"):
            st.session_state["city_input"] = st.session_state.detected_city or ""
            st.session_state["gps_just_detected"] = False

        with st.form(key="location_form", clear_on_submit=False):
            city = st.text_input(
                "🏙️ City / Town / Village",
                placeholder="e.g. Bangalore, Anekal, Mysore, Hubli",
                help="Type any city, town, or village — or use GPS above.",
                key="city_input",
            )

            st.markdown("### 🧍 Personal Health Profile")
            st.caption("Your profile personalises the health risk advice.")

            age = st.slider(
                "Age", 5, 80,
                value=st.session_state.age,
                key="age_slider",
                help="Children <12 and adults >60 are at higher pollution risk.",
            )

            asthma         = st.checkbox("🫁 Asthma",        value=st.session_state.asthma,        key="asthma_cb")
            smoker         = st.checkbox("🚬 Smoker",         value=st.session_state.smoker,         key="smoker_cb")
            outdoor_worker = st.checkbox("👷 Outdoor Worker", value=st.session_state.outdoor_worker, key="outdoor_cb")

            # Vulnerability score
            vuln_score = 0
            if age < 12 or age > 60: vuln_score += 2
            if asthma:                vuln_score += 3
            if smoker:                vuln_score += 2
            if outdoor_worker:        vuln_score += 1
            vuln_label = ("🟢 Low" if vuln_score <= 1
                          else "🟡 Moderate" if vuln_score <= 4
                          else "🔴 High")
            st.markdown(
                f"**Personal Vulnerability:** {vuln_label} &nbsp;`score: {vuln_score}/8`",
                unsafe_allow_html=True,
            )

            predict_btn = st.form_submit_button("🔍 Fetch AQI & Predict", use_container_width=True)

        # ── On Submit ──────────────────────────────────────────
        if predict_btn:
            city = st.session_state.get("city_input", "").strip()
            st.session_state.age            = age
            st.session_state.asthma         = asthma
            st.session_state.smoker         = smoker
            st.session_state.outdoor_worker = outdoor_worker
            st.session_state.vuln_score     = vuln_score

            if not city:
                st.error("⚠️ Please enter a city, town, or village name before predicting.")
            else:
                use_lat = st.session_state.detected_lat if city == st.session_state.detected_city else None
                use_lon = st.session_state.detected_lon if city == st.session_state.detected_city else None

                with st.spinner("Fetching live AQI data..."):
                    # FIX: st.info/warning shown at call site, not inside cached functions
                    live_data, fallback_msg = fetch_live_pollution(
                        city=city, lat=use_lat, lon=use_lon
                    )

                if fallback_msg:
                    if fallback_msg.startswith("⚠️"):
                        st.warning(fallback_msg)
                    else:
                        st.info(fallback_msg)

                if live_data is None:
                    st.error("❌ No monitoring station found. Try a nearby city or use GPS detection.")
                else:
                    st.session_state.pm25_history.append(live_data["pm25"])
                    st.session_state.pm25_history = st.session_state.pm25_history[-7:]

                    pred, conf = run_prediction(
                        live_data["pm25"], live_data["pm10"],
                        live_data["co"],   live_data["no2"], live_data["o3"],
                    )

                    st.session_state.aqi_history.append({
                        "time": datetime.datetime.now().strftime("%H:%M"),
                        "AQI":  live_data["aqi"],
                    })

                    st.session_state.live_data     = live_data
                    st.session_state.prediction    = pred
                    st.session_state.confidence    = conf
                    st.session_state.forecast_pred = generate_forecast(
                        live_data["pm25"], live_data["pm10"],
                        live_data["co"],   live_data["no2"], live_data["o3"],
                    )

        # ── Prediction Summary Card ──────────────────────────
        if st.session_state.live_data:
            ld   = st.session_state.live_data
            cat, cat_emoji, cat_color = aqi_category(ld["aqi"])
            st.markdown("---")
            st.markdown("#### 📋 Current Reading Summary")

            st.markdown(
                f"""<div style="background:{cat_color}22; border-left:4px solid {cat_color};
                    padding:10px 14px; border-radius:8px; margin-bottom:10px;">
                    <b style="font-size:15px;">{cat_emoji} AQI: {ld['aqi']} — {cat}</b><br>
                    <span style="color:#555; font-size:12px; font-weight:600;">
                        📡 {ld['station']}
                    </span>
                </div>""",
                unsafe_allow_html=True,
            )

            mc1, mc2 = st.columns(2)
            mc1.metric("PM2.5", f"{ld['pm25']} µg/m³")
            mc2.metric("PM10",  f"{ld['pm10']} µg/m³")
            mc3, mc4 = st.columns(2)
            mc3.metric("NO2",   f"{ld['no2']} µg/m³")
            mc4.metric("O3",    f"{ld['o3']} µg/m³")

            if st.session_state.prediction:
                pred  = st.session_state.prediction
                conf  = st.session_state.confidence
                p_emoji = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}
                p_color = {"Low": "#00c48c", "Moderate": "#f5a623", "High": "#e74c3c"}
                st.markdown(
                    f"""<div style="background:{p_color.get(pred,'#333')}22;
                        border-left:4px solid {p_color.get(pred,'#333')};
                        padding:10px 14px; border-radius:8px; margin-top:10px;">
                        <b>🤖 ML Prediction: {p_emoji.get(pred,'')} {pred} Risk</b><br>
                        <span style="color:#555; font-size:12px; font-weight:600;">
                            Confidence: {conf:.1f}%
                        </span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                # FIX: progress() expects 0.0–1.0 in Streamlit ≥1.27
                st.progress(conf / 100)

    # ── AQI Display (right column) ──────────────────────────────
    with right:
        if st.session_state.live_data:
            ld   = st.session_state.live_data
            pm25 = ld["pm25"]; pm10 = ld["pm10"]
            co   = ld["co"];   no2  = ld["no2"];  o3  = ld["o3"]
            aqi  = ld["aqi"]
            cat, cat_emoji, cat_color = aqi_category(aqi)

            st.subheader("🌍 Current AQI")

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=aqi,
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
                        "thickness": 0.8, "value": aqi,
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

            st.info(f"{cat_emoji} **AQI Category:** {cat}")

            # FIX 2: Station name — dark navy bold HTML, fully visible
            st.markdown(
                f"<p style='color:#1a3a5c !important; font-weight:700 !important; "
                f"font-size:13px; margin-top:2px;'>"
                f"📡 Station: <b>{ld['station']}</b> &nbsp;|&nbsp; 🕒 {ld['timestamp']}</p>",
                unsafe_allow_html=True,
            )

            # Grouped bar chart — measured vs WHO limit
            pollutant_df = pd.DataFrame({
                "Pollutant": ["PM2.5", "PM10", "CO", "NO2", "O3"],
                "Measured":  [pm25,    pm10,   co,   no2,   o3],
                "WHO Limit": [15,      45,     4,    25,    60],
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

    # ── Map + PM2.5 Forecast — full width below columns ────────
    if st.session_state.live_data:
        ld  = st.session_state.live_data
        aqi = ld["aqi"]

        map_col, forecast_col = st.columns(2)

        with map_col:
            if ld["lat"] != 0:
                st.subheader("🗺 Nearest AQI Monitoring Station")
                m = folium.Map(location=[ld["lat"], ld["lon"]], zoom_start=10)
                folium.Marker(
                    [ld["lat"], ld["lon"]],
                    tooltip=f"AQI: {aqi} — {cat}",
                    popup=f"<b>{ld['station']}</b><br>AQI: {aqi}<br>{ld['timestamp']}",
                    icon=folium.Icon(color="red", icon="cloud"),
                ).add_to(m)
                st_folium(m, width=None, height=350, use_container_width=True)

        with forecast_col:
            st.subheader("📈 PM2.5 Forecast Trend")
            if ld["forecast_pm25"]:
                df_fc = pd.DataFrame(ld["forecast_pm25"])
                fig3  = px.line(
                    df_fc, x="day", y="avg",
                    markers=True,
                    title="PM2.5 Daily Forecast (µg/m³)",
                    color_discrete_sequence=["#1d4ed8"],
                    template="plotly_white",
                )
                fig3.update_traces(
                    line={"width": 3, "color": "#1d4ed8"},
                    marker={"size": 9, "color": "#1d4ed8",
                            "line": {"color": "#1e3a8a", "width": 2}},
                )
                fig3.add_hline(
                    y=15,
                    line_dash="dot",
                    line_color="#b91c1c",
                    line_width=2.5,
                    annotation_text="WHO limit: 15 µg/m³",
                    annotation_position="bottom right",
                    annotation_font={"color": "#b91c1c", "size": 12},
                )
                fig3.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    font={"color": "#000000", "family": "Arial", "size": 13},
                    title_font={"color": "#000000", "size": 14},
                    xaxis={
                        "tickfont": {"color": "#000000", "size": 12},
                        "title_font": {"color": "#000000"},
                        "linecolor": "#000000",
                        "gridcolor": "#e2e8f0",
                        "title": "Day",
                    },
                    yaxis={
                        "tickfont": {"color": "#000000", "size": 12},
                        "title_font": {"color": "#000000"},
                        "linecolor": "#000000",
                        "gridcolor": "#e2e8f0",
                        "title": "PM2.5 (µg/m³)",
                    },
                    margin={"t": 60, "b": 50, "l": 60, "r": 30},
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.caption("No PM2.5 forecast data available for this station.")

        # AQI session history — Plotly for consistent theme
        if len(st.session_state.aqi_history) > 1:
            st.subheader("📊 AQI This Session")
            df_hist  = pd.DataFrame(st.session_state.aqi_history)
            fig_hist = px.line(
                df_hist, x="time", y="AQI",
                markers=True,
                title="AQI Session History",
                color_discrete_sequence=["#1d4ed8"],
                template="plotly_white",
            )
            fig_hist.update_traces(
                line={"width": 3},
                marker={"size": 9, "line": {"color": "#1e3a8a", "width": 2}},
            )
            fig_hist.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font={"color": "#000000", "family": "Arial", "size": 13},
                title_font={"color": "#000000", "size": 14},
                xaxis={"tickfont": {"color": "#000000"}, "title": "Time",  "gridcolor": "#e2e8f0"},
                yaxis={"tickfont": {"color": "#000000"}, "title": "AQI",   "gridcolor": "#e2e8f0"},
                margin={"t": 50, "b": 40, "l": 50, "r": 20},
            )
            st.plotly_chart(fig_hist, use_container_width=True)


# ================================================================
#  TAB 2 — HEALTH PREDICTION & ADVICE
# ================================================================
with tab2:
    if st.session_state.prediction is None:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.85); border-radius:12px; padding:40px;
                    text-align:center; margin-top:30px; border:1px solid #90caf9;">
            <h3 style="color:#2c5282;">Go to the Location & AQI tab first</h3>
            <p style="color:#4a90c4;">Enter a location and click <b>Fetch AQI & Predict</b>
            to see your personalised health risk assessment here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        pred           = st.session_state.prediction
        conf           = st.session_state.confidence
        vuln_score     = st.session_state.vuln_score
        ld             = st.session_state.live_data
        age            = st.session_state.age
        asthma         = st.session_state.asthma
        smoker         = st.session_state.smoker
        outdoor_worker = st.session_state.outdoor_worker

        emoji_map = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}
        color_map = {"Low": "#00c48c", "Moderate": "#f5a623", "High": "#e74c3c"}

        pred_col, advice_col = st.columns([1, 1])

        with pred_col:
            st.markdown(
                f"""<div style="background:{color_map.get(pred,'#333')};
                    border-radius:12px; padding:24px; text-align:center;">
                    <h1 style="color:white; margin:0; font-size:2.5rem;">
                        {emoji_map.get(pred,'⚪')} {pred} Risk
                    </h1>
                    <p style="color:white; margin:8px 0 0 0; font-size:15px;">
                        Model Confidence: <b>{conf:.1f}%</b>
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )
            # FIX: progress bar uses 0.0–1.0
            st.progress(conf / 100)
            st.caption(
                "Confidence = probability assigned by the Random Forest model "
                "to the predicted class."
            )

            aqi_risk_score = 2 if pred == "High" else 1 if pred == "Moderate" else 0
            combined       = vuln_score + aqi_risk_score
            combined_label = ("🔴 Very High" if combined >= 6
                              else "🟡 Elevated" if combined >= 3
                              else "🟢 Normal")
            st.metric(
                label="Combined Risk (AQI + Your Health Profile)",
                value=combined_label,
                help="AQI-based ML risk + personal vulnerability score combined.",
            )

            st.markdown("#### 🧪 Pollutant Readings")
            m1, m2, m3 = st.columns(3)
            m1.metric("PM2.5", f"{ld['pm25']}", help="WHO limit: 15 µg/m³")
            m2.metric("PM10",  f"{ld['pm10']}", help="WHO limit: 45 µg/m³")
            m3.metric("NO2",   f"{ld['no2']}",  help="WHO limit: 25 µg/m³")
            m4, m5, _ = st.columns(3)
            m4.metric("O3",    f"{ld['o3']}",   help="WHO limit: 60 µg/m³")
            m5.metric("CO",    f"{ld['co']}")

            with st.expander("🔍 Feature Values Sent to ML Model"):
                lag1, lag3, lag7, roll3, roll7 = compute_lag_features(ld["pm25"])
                st.dataframe(pd.DataFrame({
                    "Feature": [
                        "PM2.5 (current)", "PM2.5 Lag 1d", "PM2.5 Lag 3d",
                        "PM2.5 Lag 7d", "PM2.5 Roll 3d", "PM2.5 Roll 7d",
                        "NO2", "O3", "CO",
                    ],
                    "Value": [
                        round(ld["pm25"], 2), round(lag1, 2), round(lag3, 2),
                        round(lag7, 2), round(roll3, 2), round(roll7, 2),
                        round(ld["no2"], 2), round(ld["o3"], 2), round(ld["co"], 2),
                    ],
                }), hide_index=True, use_container_width=True)

        with advice_col:
            st.markdown("### 💡 Personalised Health Advice")
            tips = []

            if pred == "High":
                tips.append("⚠️ **Stay indoors** as much as possible today.")
                if outdoor_worker:
                    tips.append("👷 Wear an **N95 mask** and take frequent indoor breaks.")
                if asthma:
                    tips.append("🫁 **Asthma alert:** Keep your inhaler accessible at all times.")
                if smoker:
                    tips.append("🚬 Avoid smoking — high AQI compounds respiratory risk significantly.")
                if age > 60:
                    tips.append("👴 Elderly individuals face elevated risk. Limit all outdoor activity.")
                if age < 12:
                    tips.append("👶 Children are more vulnerable. Keep them indoors and windows closed.")
            elif pred == "Moderate":
                tips.append("🟡 Air quality is moderate. Limit prolonged outdoor exertion.")
                if asthma:
                    tips.append("🫁 Carry your medication — sensitive groups may feel discomfort outdoors.")
                if outdoor_worker:
                    tips.append("👷 Take regular breaks and stay hydrated if working outside.")
                if age > 60 or age < 12:
                    tips.append("⚠️ Sensitive age group — consider reducing outdoor time today.")
            else:
                tips.append("✅ Air quality is good. Outdoor activities are safe.")
                if asthma:
                    tips.append("🫁 Still monitor your breathing — brief local spikes can occur.")
                tips.append("💧 Stay hydrated and maintain general wellness practices.")

            for tip in tips:
                st.markdown(f"- {tip}")

            st.markdown("### 📅 3-Day Health Risk Forecast")
            if st.session_state.forecast_pred:
                for day_label, risk in st.session_state.forecast_pred:
                    e = emoji_map.get(risk, "⚪")
                    c = color_map.get(risk, "#333")
                    st.markdown(
                        f'<div style="background:{c}22; border-left:4px solid {c}; '
                        f'padding:8px 14px; border-radius:6px; margin-bottom:6px;">'
                        f'<b>{day_label}</b> &nbsp; {e} {risk}</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("### 📄 Download Report")
            report = f"""AIR QUALITY HEALTH RISK REPORT
================================
Generated   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Station     : {ld['station']}
Last Updated: {ld['timestamp']}

POLLUTANT READINGS
------------------
AQI   : {ld['aqi']}  ({aqi_category(ld['aqi'])[0]})
PM2.5 : {ld['pm25']} µg/m³  (WHO limit: 15)
PM10  : {ld['pm10']} µg/m³  (WHO limit: 45)
CO    : {ld['co']}
NO2   : {ld['no2']} µg/m³   (WHO limit: 25)
O3    : {ld['o3']} µg/m³    (WHO limit: 60)
SO2   : {ld.get('so2', 'N/A')}
NH3   : {ld.get('nh3', 'N/A')}

PERSONAL HEALTH PROFILE
------------------------
Age            : {age}
Asthma         : {'Yes' if asthma else 'No'}
Smoker         : {'Yes' if smoker else 'No'}
Outdoor Worker : {'Yes' if outdoor_worker else 'No'}
Vulnerability  : {vuln_score}/8

ML PREDICTION
-------------
Health Risk : {pred}
Confidence  : {conf:.1f}%
Combined    : {combined_label}

3-DAY FORECAST
--------------
"""
            for day_label, risk in st.session_state.forecast_pred:
                report += f"{day_label}: {risk}\n"

            report += "\nPersonalised Advice:\n"
            for tip in tips:
                report += f"  • {tip.replace('**','').replace('*','')}\n"

            st.download_button(
                label="⬇️ Download Health Report (.txt)",
                data=report,
                file_name=f"aqi_health_report_{datetime.date.today()}.txt",
                mime="text/plain",
                use_container_width=True,
            )

# ============================================================
# ============================================================
# AIRSEVA AGENT SECTION — ADDED
# ============================================================
with tab3:
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