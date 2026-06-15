import os
import requests

def get_granite_advisory(city: str, aqi: int, risk_level: str, pollutants: dict, vulnerability_score: int) -> str:
    """
    Calls IBM Granite-13b-chat-v2 on WatsonX (Frankfurt) for air quality
    health advisory. This is the sole advisory LLM for AirSeva.
    """
    api_key = os.environ.get("WATSONX_API_KEY", "")
    project_id = os.environ.get("WATSONX_PROJECT_ID", "")

    if not api_key or not project_id:
        return "IBM Granite advisory unavailable: API credentials not configured."

    # Step 1: Get IAM token
    try:
        iam_resp = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
            timeout=15
        )
        iam_resp.raise_for_status()
        iam_token = iam_resp.json()["access_token"]
    except Exception as e:
        return f"IBM Granite advisory unavailable: Authentication failed ({str(e)})."

    # Step 2: Build prompt
    pollutant_str = ", ".join([f"{k.upper()}: {v}" for k, v in pollutants.items()])
    prompt = f"""You are an air quality health advisor for Indian communities.

City: {city}
AQI: {aqi}
Risk Level: {risk_level}
Pollutants: {pollutant_str}
Personal Vulnerability Score: {vulnerability_score}/8

Provide a concise, practical health advisory in 4-5 sentences. Include:
1. Overall air quality assessment for this city
2. Specific health precautions based on the risk level
3. Who is most at risk given the vulnerability score
4. One actionable recommendation for today

Advisory:"""

    # Step 3: Call WatsonX Granite
    try:
        wx_resp = requests.post(
            "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29",
            headers={
                "Authorization": f"Bearer {iam_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "model_id": "ibm/granite-13b-chat-v2",
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 300,
                    "min_new_tokens": 50,
                    "repetition_penalty": 1.1
                },
                "project_id": project_id
            },
            timeout=30
        )
        wx_resp.raise_for_status()
        result = wx_resp.json()
        generated = result["results"][0]["generated_text"].strip()
        return generated if generated else "IBM Granite returned an empty response."
    except Exception as e:
        return f"IBM Granite advisory unavailable: Model call failed ({str(e)})."
