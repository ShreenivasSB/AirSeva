import os
import logging
from granite_advisory import get_granite_advisory

logger = logging.getLogger(__name__)

def generate_advisory(city: str, aqi: int, risk_level: str, pollutants: dict, vulnerability_score: int) -> str:
    """
    Agent 3 — Advisory Agent.
    Generates a personalised air quality health advisory using IBM Granite 4
    via IBM WatsonX AI (Frankfurt region).
    """
    logger.info(f"Agent 3: Generating IBM Granite advisory for {city}, AQI={aqi}")
    
    if not os.getenv("WATSONX_API_KEY"):
        return "WATSONX_API_KEY environment variable is missing. Cannot call IBM WatsonX API."
    
    if not os.getenv("WATSONX_PROJECT_ID"):
        return "WATSONX_PROJECT_ID environment variable is missing. Cannot call IBM WatsonX API."
    
    advisory = get_granite_advisory(
        city=city,
        aqi=aqi,
        risk_level=risk_level,
        pollutants=pollutants,
        vulnerability_score=vulnerability_score
    )
    
    logger.info("Agent 3: IBM Granite advisory generated successfully.")
    return advisory
