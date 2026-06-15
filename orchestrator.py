import os
import logging

# 8. Use logging throughout with format: "%(asctime)s [AirSeva] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AirSeva] %(message)s"
)
logger = logging.getLogger("AirSeva")

# 1. Load environment variables from .env file using python-dotenv at startup
from dotenv import load_dotenv
load_dotenv()
# Also make sure the .env file is loaded if executed from other directories
if not os.getenv("WAQI_TOKEN"):
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Rules: Load .env before any agent imports
from agents.agent_1_data_fetcher import fetch_data
from agents.agent_2_ml_prediction import predict
from agents.agent_3_advisory import generate_advisory
from agents.agent_4_report import compile_report, report_to_text


# 2. Define main function
def run_airseva(
    city: str,
    vulnerability_score: int = 0
) -> dict:
    """
    Orchestrates the AirSeva 4-agent agentic AI system.
    
    Runs 4 agents in sequence, logs completion at each step,
    handles errors cleanly by logging and re-raising, prints the human-readable
    report summary, and returns the final report dictionary.
    """
    logger.info(f"Starting AirSeva run for city: {city} with vulnerability score: {vulnerability_score}")

    # Step 1: Call fetch_data(city)
    try:
        agent1_output = fetch_data(city)
    except Exception as e:
        logger.error(f"Agent 1 failed — {e}")
        raise e
    logger.info(f"Agent 1 complete — data fetched for {city}")

    # Step 2: Call predict(agent1_output)
    try:
        agent2_output = predict(agent1_output)
    except Exception as e:
        logger.error(f"Agent 2 failed — {e}")
        raise e
    
    risk_level = agent2_output.get("risk_level")
    confidence = agent2_output.get("confidence")
    logger.info(f"Agent 2 complete — Risk: {risk_level}, Confidence: {confidence}%")

    # Step 3: Call generate_advisory(...)
    try:
        agent3_output = generate_advisory(
            city=agent1_output.get("city", city),
            aqi=agent1_output.get("aqi_value", 0),
            risk_level=agent2_output.get("risk_level", "Low"),
            pollutants=agent1_output.get("pollutants", {}),
            vulnerability_score=vulnerability_score
        )
    except Exception as e:
        logger.error(f"Agent 3 failed — {e}")
        raise e
    logger.info("Agent 3 complete — advisory generated")

    # Step 4: Call compile_report(...)
    try:
        report = compile_report(
            agent1_output,
            agent2_output,
            agent3_output
        )
    except Exception as e:
        logger.error(f"Agent 4 failed — {e}")
        raise e
    logger.info("Agent 4 complete — report compiled")

    # 5. Also print the full report_to_text() output to console at the end
    print(report_to_text(report))

    # 4. Return the final report dict from Agent 4
    return report


# 7. Add this block at the bottom
if __name__ == "__main__":
    import sys
    city = sys.argv[1] if len(sys.argv) > 1 else "Delhi"
    score = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    result = run_airseva(city, score)
