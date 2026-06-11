import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger("agent_3_advisory")
# In case this file is run directly or logger is not configured
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


def generate_advisory(
    agent1_output: dict,
    agent2_output: dict,
    vulnerability_score: int
) -> dict:
    """
    Generates a personalised air quality health advisory using Gemini 2.5 Flash model
    based on live AQI data, ML risk prediction, and user's vulnerability score.
    
    Args:
        agent1_output (dict): Data from Agent 1 (live AQI, city, pollutants).
        agent2_output (dict): Predictions from Agent 2 (risk_level, confidence).
        vulnerability_score (int): Score between 0 and 8.
        
    Returns:
        dict: A dictionary containing the generated advisory text and metadata.
    """
    logger.info("Starting health advisory generation...")

    # Step 1: Verify GEMINI_API_KEY is present
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        error_msg = "GEMINI_API_KEY environment variable is missing. Cannot call Gemini API."
        logger.critical(error_msg)
        raise EnvironmentError(error_msg)

    # Step 2: Validate vulnerability score and map to profile
    if not isinstance(vulnerability_score, int) or not (0 <= vulnerability_score <= 8):
        error_msg = f"Vulnerability score must be an integer between 0 and 8, got: {vulnerability_score}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if 0 <= vulnerability_score <= 2:
        vulnerability_profile = "Healthy adult (low vulnerability)"
    elif 3 <= vulnerability_score <= 5:
        vulnerability_profile = "Moderate vulnerability (elderly, mild asthma, children)"
    else:  # 6-8
        vulnerability_profile = "High vulnerability (severe respiratory/cardiac conditions, pregnant women, infants)"

    logger.info(f"Mapped vulnerability score {vulnerability_score} to profile: '{vulnerability_profile}'")

    # Step 3: Extract values from Agent 1 and Agent 2 outputs
    city = agent1_output.get("city")
    aqi_value = agent1_output.get("aqi_value")
    pm25 = agent1_output.get("pm25")
    pm10 = agent1_output.get("pm10")
    
    risk_level = agent2_output.get("risk_level")
    confidence = agent2_output.get("confidence")

    logger.info(f"Input details - City: {city}, AQI: {aqi_value}, Risk: {risk_level}")

    # Step 4: Build the prompt
    prompt = f"""You are AirSeva, an AI health advisor for Indian communities. Generate a personalised air quality health advisory in clear, simple English suitable for general public.

City: {city}
Current AQI: {aqi_value}
PM2.5 Level: {pm25} µg/m³
PM10 Level: {pm10} µg/m³
Health Risk Level: {risk_level}
Model Confidence: {confidence}%
Vulnerability Score: {vulnerability_score}/8

Vulnerability Profile: {vulnerability_profile}

Provide:
1. A 2-line plain-language summary of current air quality
2. Specific health precautions for this vulnerability profile
3. Recommended outdoor activity guidance
4. Indoor air quality tips
5. When to seek medical attention

Keep total response under 300 words.
Use simple language, no jargon.
Format with clear numbered sections."""

    # Step 5: Initialize Gemini Client and call generate_content
    logger.info("Initializing google-genai client...")
    try:
        # Client will automatically read GEMINI_API_KEY from environment.
        # Ensure it is explicitly in os.environ for the SDK to read.
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        client = genai.Client()
    except Exception as e:
        error_msg = f"Failed to initialize google-genai client: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    logger.info("Calling Gemini API (gemini-2.5-flash) to generate content...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        advisory_text = response.text
    except Exception as e:
        error_msg = f"Gemini API call failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    if not advisory_text:
        error_msg = "Gemini API returned empty response."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info("Advisory generated successfully.")

    # Step 6: Construct and return the output dictionary
    return {
        'advisory': advisory_text,
        'city': city,
        'risk_level': risk_level,
        'vulnerability_score': vulnerability_score,
        'vulnerability_profile': vulnerability_profile
    }
