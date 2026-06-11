import datetime
import logging

# Configure logger
logger = logging.getLogger("agent_4_report")
# In case this file is run directly or logger is not configured
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# WHO Limits (2021 guidelines)
# pm25_24h = 15.0 µg/m³
# pm10_24h = 45.0 µg/m³
# no2_annual = 10.0 µg/m³
# so2_24h = 40.0 µg/m³
# co_8h = 4.0 mg/m³
# o3_8h = 60.0 µg/m³
WHO_LIMITS = {
    'pm25_24h': 15.0,
    'pm10_24h': 45.0,
    'no2_annual': 10.0,
    'so2_24h': 40.0,
    'co_8h': 4.0,
    'o3_8h': 60.0
}


def compile_report(
    agent1_output: dict,
    agent2_output: dict,
    agent3_output: dict
) -> dict:
    """
    Validates outputs from the first three agents, checks pollutant concentrations
    against WHO 2021 limits, and compiles a comprehensive health risk report.
    
    Args:
        agent1_output (dict): Data from Agent 1 (live AQI, city, pollutants).
        agent2_output (dict): Predictions from Agent 2 (risk_level, confidence, probabilities).
        agent3_output (dict): Advisory from Agent 3 (advisory, vulnerability).
        
    Returns:
        dict: A structured report dictionary.
    """
    logger.info("Compiling final air quality health risk report...")

    # Step 1: Validate input keys
    required_agent1 = ['city', 'aqi_value', 'pm25', 'pm10', 'no2', 'so2', 'co', 'o3']
    for k in required_agent1:
        if k not in agent1_output:
            error_msg = f"Required key '{k}' missing from agent1_output"
            logger.error(error_msg)
            raise KeyError(error_msg)

    required_agent2 = ['risk_level', 'confidence', 'probabilities']
    for k in required_agent2:
        if k not in agent2_output:
            error_msg = f"Required key '{k}' missing from agent2_output"
            logger.error(error_msg)
            raise KeyError(error_msg)

    required_agent3 = ['vulnerability_score', 'vulnerability_profile', 'advisory']
    for k in required_agent3:
        if k not in agent3_output:
            error_msg = f"Required key '{k}' missing from agent3_output"
            logger.error(error_msg)
            raise KeyError(error_msg)

    logger.info("All inputs validated successfully.")

    # Step 2: Extract values and cast appropriately
    pm25 = float(agent1_output['pm25'])
    pm10 = float(agent1_output['pm10'])
    no2 = float(agent1_output['no2'])
    so2 = float(agent1_output['so2'])
    co = float(agent1_output['co'])
    o3 = float(agent1_output['o3'])

    # Step 3: Compute WHO exceedances
    who_exceedances = {
        'pm25': pm25 > WHO_LIMITS['pm25_24h'],
        'pm10': pm10 > WHO_LIMITS['pm10_24h'],
        'no2': no2 > WHO_LIMITS['no2_annual'],
        'so2': so2 > WHO_LIMITS['so2_24h'],
        'co': co > WHO_LIMITS['co_8h'],
        'o3': o3 > WHO_LIMITS['o3_8h']
    }

    # Step 4: Generate timestamp in India Standard Time (IST)
    tz_ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    timestamp = datetime.datetime.now(tz_ist).isoformat()

    logger.info(f"Report compiled at {timestamp} for city: {agent1_output['city']}")

    # Step 5: Construct structured report
    report = {
        'timestamp': timestamp,
        'city': agent1_output['city'],
        'aqi_value': int(agent1_output['aqi_value']),
        'risk_level': agent2_output['risk_level'],
        'confidence': float(agent2_output['confidence']),
        'vulnerability_score': int(agent3_output['vulnerability_score']),
        'vulnerability_profile': agent3_output['vulnerability_profile'],
        'pollutants': {
            'pm25': pm25,
            'pm10': pm10,
            'no2': no2,
            'so2': so2,
            'co': co,
            'o3': o3
        },
        'who_limits': WHO_LIMITS.copy(),
        'who_exceedances': who_exceedances,
        'advisory': agent3_output['advisory'],
        'model_probabilities': agent2_output['probabilities'],
        'data_source': 'WAQI API + Open-Meteo',
        'model_info': {
            'name': 'Random Forest Classifier',
            'features_used': 22,
            'sklearn_version': '1.8.0'
        }
    }

    return report


def report_to_text(report: dict) -> str:
    """
    Converts a compiled report dictionary into a clean, human-readable text summary
    including clear section labels and WHO guideline warnings.
    
    Args:
        report (dict): Compiled report from compile_report.
        
    Returns:
        str: Clean readable text summary.
    """
    logger.info("Formatting report to text...")
    
    pollutants = report['pollutants']
    who_limits = report['who_limits']
    exceedances = report['who_exceedances']

    # Build warnings text block
    warnings_list = []
    for pollutant, exceeded in exceedances.items():
        if exceeded:
            val = pollutants[pollutant]
            unit = "mg/m³" if pollutant == 'co' else "µg/m³"
            limit_key = f"{pollutant}_24h" if f"{pollutant}_24h" in who_limits else (f"{pollutant}_annual" if f"{pollutant}_annual" in who_limits else f"{pollutant}_8h")
            limit = who_limits[limit_key]
            warnings_list.append(f"  [!] WARNING: {pollutant.upper()} concentration ({val} {unit}) exceeds WHO limit of {limit} {unit}")
            
    if warnings_list:
        warnings_str = "\n".join(warnings_list)
    else:
        warnings_str = "  [+] All pollutant readings are within WHO 2021 air quality guidelines."

    text = f"""======================================================================
                  AIRSEVA AIR QUALITY HEALTH REPORT
======================================================================
Generated Timestamp : {report['timestamp']}
Data Source         : {report['data_source']}

----------------------------------------------------------------------
1. MONITORING SITE & SUMMARY DETAILS
----------------------------------------------------------------------
City Name           : {report['city']}
Current Air Quality : AQI = {report['aqi_value']}
Health Risk level   : {report['risk_level']} (Model Confidence: {report['confidence']}%)

----------------------------------------------------------------------
2. RECIPIENT VULNERABILITY LEVEL
----------------------------------------------------------------------
Vulnerability Score : {report['vulnerability_score']}/8
Assigned Profile    : {report['vulnerability_profile']}

----------------------------------------------------------------------
3. CHEMICAL POLLUTANT READINGS & WHO STANDARDS
----------------------------------------------------------------------
Current Readings:
  - PM2.5: {pollutants['pm25']} µg/m³ (WHO Limit: {who_limits['pm25_24h']} µg/m³)
  - PM10:  {pollutants['pm10']} µg/m³ (WHO Limit: {who_limits['pm10_24h']} µg/m³)
  - NO2:   {pollutants['no2']} µg/m³ (WHO Limit: {who_limits['no2_annual']} µg/m³)
  - SO2:   {pollutants['so2']} µg/m³ (WHO Limit: {who_limits['so2_24h']} µg/m³)
  - CO:    {pollutants['co']} mg/m³ (WHO Limit: {who_limits['co_8h']} mg/m³)
  - O3:    {pollutants['o3']} µg/m³ (WHO Limit: {who_limits['o3_8h']} µg/m³)

Guidelines Status:
{warnings_str}

----------------------------------------------------------------------
4. PERSONALIZED HEALTH ADVISORY (AirSeva)
----------------------------------------------------------------------
{report['advisory'].strip()}

----------------------------------------------------------------------
5. MACHINE LEARNING DIAGNOSTICS
----------------------------------------------------------------------
Predictive Model    : {report['model_info']['name']}
Features Processed  : {report['model_info']['features_used']}
Model Version       : scikit-learn {report['model_info']['sklearn_version']}
Class Probabilities :
  - High: {report['model_probabilities']['High']:.4f}
  - Low: {report['model_probabilities']['Low']:.4f}
  - Moderate: {report['model_probabilities']['Moderate']:.4f}

======================================================================
"""
    return text
