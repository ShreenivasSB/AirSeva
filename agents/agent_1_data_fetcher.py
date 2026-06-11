import os
import logging
import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

# Configure logger for this module
logger = logging.getLogger("agent_1_data_fetcher")
# In case this file is run directly or logger is not configured
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Load environment variables. We try loading standard dotenv,
# but also look up the current working directory explicitly to support direct execution.
load_dotenv()
if not os.getenv("WAQI_TOKEN"):
    # Fallback to current working directory or parent directories if run from scratch space
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Read token
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

# Canonical mapping database for the 26 supported Indian cities
CITY_DATA = {
    "ahmedabad": {
        "name": "Ahmedabad",
        "coords": (23.0225, 72.5714),
        "encoded": 0,
        "slug": "ahmedabad"
    },
    "aizawl": {
        "name": "Aizawl",
        "coords": (23.7271, 92.7176),
        "encoded": 1,
        "slug": "aizawl"
    },
    "amaravati": {
        "name": "Amaravati",
        "coords": (16.5730, 80.3582),
        "encoded": 2,
        "slug": "amaravati"
    },
    "amritsar": {
        "name": "Amritsar",
        "coords": (31.6340, 74.8723),
        "encoded": 3,
        "slug": "amritsar"
    },
    "bengaluru": {
        "name": "Bengaluru",
        "coords": (12.9716, 77.5946),
        "encoded": 4,
        "slug": "bangalore"
    },
    "bhopal": {
        "name": "Bhopal",
        "coords": (23.2599, 77.4126),
        "encoded": 5,
        "slug": "bhopal"
    },
    "brajrajnagar": {
        "name": "Brajrajnagar",
        "coords": (21.8167, 83.9167),
        "encoded": 6,
        "slug": "brajrajnagar"
    },
    "chandigarh": {
        "name": "Chandigarh",
        "coords": (30.7333, 76.7794),
        "encoded": 7,
        "slug": "chandigarh"
    },
    "chennai": {
        "name": "Chennai",
        "coords": (13.0827, 80.2707),
        "encoded": 8,
        "slug": "chennai"
    },
    "coimbatore": {
        "name": "Coimbatore",
        "coords": (11.0168, 76.9558),
        "encoded": 9,
        "slug": "coimbatore"
    },
    "delhi": {
        "name": "Delhi",
        "coords": (28.7041, 77.1025),
        "encoded": 10,
        "slug": "delhi"
    },
    "ernakulam": {
        "name": "Ernakulam",
        "coords": (9.9816, 76.2999),
        "encoded": 11,
        "slug": "ernakulam"
    },
    "gurugram": {
        "name": "Gurugram",
        "coords": (28.4595, 77.0266),
        "encoded": 12,
        "slug": "gurgaon"
    },
    "guwahati": {
        "name": "Guwahati",
        "coords": (26.1445, 91.7362),
        "encoded": 13,
        "slug": "guwahati"
    },
    "hyderabad": {
        "name": "Hyderabad",
        "coords": (17.3850, 78.4867),
        "encoded": 14,
        "slug": "hyderabad"
    },
    "jaipur": {
        "name": "Jaipur",
        "coords": (26.9124, 75.7873),
        "encoded": 15,
        "slug": "jaipur"
    },
    "jorapokhar": {
        "name": "Jorapokhar",
        "coords": (23.6800, 86.4200),
        "encoded": 16,
        "slug": "jorapokhar"
    },
    "kochi": {
        "name": "Kochi",
        "coords": (9.9312, 76.2673),
        "encoded": 17,
        "slug": "kochi"
    },
    "kolkata": {
        "name": "Kolkata",
        "coords": (22.5726, 88.3639),
        "encoded": 18,
        "slug": "kolkata"
    },
    "lucknow": {
        "name": "Lucknow",
        "coords": (26.8467, 80.9462),
        "encoded": 19,
        "slug": "lucknow"
    },
    "mumbai": {
        "name": "Mumbai",
        "coords": (19.0760, 72.8777),
        "encoded": 20,
        "slug": "mumbai"
    },
    "patna": {
        "name": "Patna",
        "coords": (25.5941, 85.1376),
        "encoded": 21,
        "slug": "patna"
    },
    "shillong": {
        "name": "Shillong",
        "coords": (25.5788, 91.8933),
        "encoded": 22,
        "slug": "shillong"
    },
    "talcher": {
        "name": "Talcher",
        "coords": (20.9500, 85.2333),
        "encoded": 23,
        "slug": "talcher"
    },
    "thiruvananthapuram": {
        "name": "Thiruvananthapuram",
        "coords": (8.5241, 76.9366),
        "encoded": 24,
        "slug": "thiruvananthapuram"
    },
    "visakhapatnam": {
        "name": "Visakhapatnam",
        "coords": (17.6868, 83.2185),
        "encoded": 25,
        "slug": "visakhapatnam"
    }
}

# Imputation constants for features WAQI does not provide
IMPUTED_NO = 17.8050
IMPUTED_NOX = 32.3319
IMPUTED_NH3 = 23.3930
IMPUTED_TOLUENE = 8.7103
IMPUTED_XYLENE = 3.1733


def fetch_data(city: str) -> dict:
    """
    Fetches live air quality data from WAQI API and historical PM2.5 from Open-Meteo
    to construct feature inputs for the Air Quality Health Risk Predictor model.
    
    Args:
        city (str): The name of the city.
        
    Returns:
        dict: A dictionary containing 22 ordered features plus 'aqi_value' and 'city'.
    """
    logger.info(f"Starting data fetch for city: '{city}'")
    
    # Step 1: Normalize city name and resolve canonical details
    city_clean = city.strip().lower()
    if city_clean not in CITY_DATA:
        error_msg = f"City '{city}' is not supported."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    city_info = CITY_DATA[city_clean]
    canonical_name = city_info["name"]
    city_slug = city_info["slug"]
    lat, lon = city_info["coords"]
    city_encoded = city_info["encoded"]
    
    logger.info(f"Resolved canonical city: '{canonical_name}' (Slug: '{city_slug}', Coordinates: {lat}, {lon})")

    # Step 2: Ensure WAQI token is set
    if not WAQI_TOKEN:
        error_msg = "WAQI_TOKEN environment variable is missing. Cannot fetch live AQI data."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Step 3: Fetch live AQI data from WAQI API
    waqi_url_requested = f"https://api.waqi.info/feed/@{city_slug}/?token={WAQI_TOKEN}"
    waqi_url_fallback = f"https://api.waqi.info/feed/{city_slug}/?token={WAQI_TOKEN}"
    
    logger.info("Fetching live AQI from WAQI API...")
    try:
        # We try the requested URL format first
        logger.info(f"Attempting requested URL format: {waqi_url_requested}")
        response = requests.get(waqi_url_requested, timeout=10)
        response.raise_for_status()
        waqi_response = response.json()
        
        # If it returns "Unknown station" or fails, we fallback to the working format without '@'
        if waqi_response.get("status") != "ok" and "Unknown station" in str(waqi_response.get("data", "")):
            logger.warning("Requested URL format failed with 'Unknown station'. Retrying without '@' prefix...")
            logger.info(f"Attempting working URL format: {waqi_url_fallback}")
            response = requests.get(waqi_url_fallback, timeout=10)
            response.raise_for_status()
            waqi_response = response.json()
            
    except Exception as e:
        error_msg = f"WAQI API connection failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    if waqi_response.get("status") != "ok":
        error_msg = f"WAQI API returned non-ok status. Detail: {waqi_response.get('data', 'Unknown error')}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Step 4: Parse pollutants from WAQI response
    data_block = waqi_response.get("data", {})
    iaqi_block = data_block.get("iaqi", {})
    
    # Extract raw AQI
    raw_aqi = data_block.get("aqi")
    try:
        aqi_value = int(raw_aqi) if raw_aqi is not None else 0
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse raw AQI value '{raw_aqi}' as integer. Falling back to 0.")
        aqi_value = 0

    def get_pollutant_val(key: str, default: float = 0.0) -> float:
        val_dict = iaqi_block.get(key)
        if isinstance(val_dict, dict):
            val = val_dict.get("v")
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    logger.warning(f"Could not cast pollutant '{key}' value '{val}' to float. Using fallback.")
        return default

    pm25 = get_pollutant_val("pm25")
    pm10 = get_pollutant_val("pm10")
    no2 = get_pollutant_val("no2")
    so2 = get_pollutant_val("so2")
    co = get_pollutant_val("co")
    o3 = get_pollutant_val("o3")
    benzene = get_pollutant_val("benzene", 0.0)

    logger.info(f"Live pollutants fetched: pm25={pm25}, pm10={pm10}, no2={no2}, so2={so2}, co={co}, o3={o3}, benzene={benzene}")

    # Step 5: Fetch 7-day historical hourly PM2.5 from Open-Meteo Air Quality API
    open_meteo_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    om_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5",
        "past_days": 7,
        "forecast_days": 1
    }
    
    pm25_history = []
    logger.info("Fetching historical hourly PM2.5 from Open-Meteo Air Quality API...")
    try:
        om_response = requests.get(open_meteo_url, params=om_params, timeout=10)
        om_response.raise_for_status()
        om_data = om_response.json()
        pm25_history = om_data.get("hourly", {}).get("pm2_5", [])
    except Exception as e:
        logger.warning(f"Failed to fetch historical hourly PM2.5 from Open-Meteo: {e}. Will fallback to current pm25.")

    # Step 6: Compute lag and rolling features using pandas
    logger.info("Computing lag and rolling features...")
    try:
        s = pd.Series(pm25_history)
        s = s.dropna().reset_index(drop=True)
        
        def get_lag_val(series: pd.Series, lag_hours: int, fallback: float) -> float:
            if len(series) > lag_hours:
                val = series.shift(lag_hours).iloc[-1]
                if not pd.isna(val):
                    return float(val)
            return fallback

        def get_roll_val(series: pd.Series, window_hours: int, fallback: float) -> float:
            if len(series) >= window_hours:
                val = series.rolling(window_hours).mean().iloc[-1]
                if not pd.isna(val):
                    return float(val)
            return fallback

        pm25_lag_1 = get_lag_val(s, 24, pm25)
        pm25_lag_3 = get_lag_val(s, 72, pm25)
        pm25_lag_7 = get_lag_val(s, 168, pm25)
        pm25_roll_3 = get_roll_val(s, 72, pm25)
        pm25_roll_7 = get_roll_val(s, 168, pm25)
    except Exception as e:
        logger.warning(f"Error computing lag/rolling features: {e}. Falling back to current pm25 value.")
        pm25_lag_1 = pm25
        pm25_lag_3 = pm25
        pm25_lag_7 = pm25
        pm25_roll_3 = pm25
        pm25_roll_7 = pm25

    logger.info(f"Lags: lag_1={pm25_lag_1}, lag_3={pm25_lag_3}, lag_7={pm25_lag_7}")
    logger.info(f"Rolls: roll_3={pm25_roll_3}, roll_7={pm25_roll_7}")

    # Step 7: Calculate datetime features in India Standard Time (IST)
    tz_ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now_ist = datetime.datetime.now(tz_ist)
    year = now_ist.year
    month = now_ist.month
    day = now_ist.day
    day_of_week = now_ist.weekday()
    
    logger.info(f"Computed IST datetime features: Year={year}, Month={month}, Day={day}, DayOfWeek={day_of_week}")

    # Step 8: Return the final dictionary with EXACTLY the requested keys and order
    result_dict = {
        "pm25": pm25,
        "pm10": pm10,
        "no": IMPUTED_NO,
        "no2": no2,
        "nox": IMPUTED_NOX,
        "nh3": IMPUTED_NH3,
        "co": co,
        "so2": so2,
        "o3": o3,
        "benzene": benzene,
        "toluene": IMPUTED_TOLUENE,
        "xylene": IMPUTED_XYLENE,
        "city_encoded": city_encoded,
        "pm25_lag_1": pm25_lag_1,
        "pm25_lag_3": pm25_lag_3,
        "pm25_lag_7": pm25_lag_7,
        "pm25_roll_3": pm25_roll_3,
        "pm25_roll_7": pm25_roll_7,
        "year": year,
        "month": month,
        "day": day,
        "day_of_week": day_of_week,
        "aqi_value": aqi_value,
        "city": city
    }
    
    logger.info(f"Data fetch completed successfully for '{city}'")
    return result_dict
