import joblib

try:
    model = joblib.load('models/health_risk_rf_model.pkl')
    print('Model loaded successfully')
    print('Classes:', model.classes_)
    print('Features:', model.feature_names_in_.tolist())
    print('Feature count:', len(model.feature_names_in_))
except Exception as e:
    print('Error:', e)