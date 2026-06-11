import os
import logging
import joblib
import pandas as pd

# Configure logger
logger = logging.getLogger("agent_2_ml_prediction")
# In case this file is run directly or logger is not configured
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Resolve model path relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "health_risk_rf_model.pkl")

logger.info(f"Loading ML model from path: {MODEL_PATH}")
if not os.path.exists(MODEL_PATH):
    error_msg = f"Model file not found at: {MODEL_PATH}"
    logger.critical(error_msg)
    raise FileNotFoundError(error_msg)

try:
    model = joblib.load(MODEL_PATH)
    logger.info("Model loaded successfully.")
except Exception as e:
    error_msg = f"Failed to load model from path {MODEL_PATH}: {e}"
    logger.critical(error_msg)
    raise RuntimeError(error_msg) from e

# Define the exact expected features and order
EXPECTED_FEATURES = [
    'pm25', 'pm10', 'no', 'no2', 'nox', 'nh3', 'co', 'so2', 'o3',
    'benzene', 'toluene', 'xylene', 'city_encoded', 'pm25_lag_1',
    'pm25_lag_3', 'pm25_lag_7', 'pm25_roll_3', 'pm25_roll_7',
    'year', 'month', 'day', 'day_of_week'
]

# Label mapping
RISK_LABEL_MAP = {0: 'High', 1: 'Low', 2: 'Moderate'}


def predict(agent1_output: dict) -> dict:
    """
    Accepts the output from Agent 1, validates and extracts the 22 ML features,
    and runs prediction using the pre-loaded Random Forest model.
    
    Args:
        agent1_output (dict): Output from Agent 1 containing 22 ML features plus metadata.
        
    Returns:
        dict: A dictionary containing prediction risk level, confidence, and probabilities.
    """
    logger.info("Starting prediction process...")
    
    if not isinstance(agent1_output, dict):
        error_msg = f"Input must be a dictionary, got: {type(agent1_output)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Validate presence of required features
    missing_features = [f for f in EXPECTED_FEATURES if f not in agent1_output]
    if missing_features:
        error_msg = f"Input dictionary is missing required features: {missing_features}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    # Build the feature dict in exact order
    model_input = {f: agent1_output[f] for f in EXPECTED_FEATURES}
    
    # Feature count check
    if len(model_input) != 22:
        error_msg = f"Expected exactly 22 features for model input, got: {len(model_input)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Build pandas DataFrame
    logger.info("Constructing DataFrame for model prediction...")
    df = pd.DataFrame([model_input])[EXPECTED_FEATURES]
    
    # Run prediction
    logger.info("Running model inference...")
    try:
        pred_val = model.predict(df)[0]
        proba_list = model.predict_proba(df)[0]
    except Exception as e:
        error_msg = f"Error during model prediction: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    # Map prediction value
    # If the model returns an integer (or integer-like value), use the mapping
    try:
        pred_int = int(pred_val)
        if pred_int not in RISK_LABEL_MAP:
            error_msg = f"Model prediction integer '{pred_int}' is not recognized in label mapping."
            logger.error(error_msg)
            raise ValueError(error_msg)
        risk_level = RISK_LABEL_MAP[pred_int]
    except (ValueError, TypeError):
        # Otherwise, if it is already a string label (e.g. 'High', 'Low', 'Moderate'), use it directly
        risk_level = str(pred_val)

    # Calculate confidence score: max probability * 100, rounded to 2 decimal places
    max_prob = max(proba_list)
    confidence = round(float(max_prob) * 100, 2)
    
    # Map classes to label probabilities
    class_to_idx = {cls: i for i, cls in enumerate(model.classes_)}
    
    def get_prob(label, integer_class):
        if label in class_to_idx:
            return float(proba_list[class_to_idx[label]])
        elif integer_class in class_to_idx:
            return float(proba_list[class_to_idx[integer_class]])
        elif str(integer_class) in class_to_idx:
            return float(proba_list[class_to_idx[str(integer_class)]])
        else:
            logger.warning(f"Could not find class index for label='{label}' / class='{integer_class}' in model classes: {model.classes_}")
            return 0.0

    probabilities = {
        'High': get_prob('High', 0),
        'Low': get_prob('Low', 1),
        'Moderate': get_prob('Moderate', 2)
    }
    
    logger.info(f"Prediction result: Risk Level = {risk_level}, Confidence = {confidence}%")
    
    return {
        'risk_level': risk_level,
        'confidence': confidence,
        'probabilities': probabilities,
        'model_input_features': model_input
    }
