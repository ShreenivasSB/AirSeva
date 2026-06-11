import pandas as pd
import joblib

df = pd.read_csv('data/city_day_cleaned.csv')
model = joblib.load('models/health_risk_rf_model.pkl')

# Recreate encoding exactly as feature engineering did
df['city_encoded'] = df['city'].astype('category').cat.codes
mapping = df[['city', 'city_encoded']].drop_duplicates().sort_values('city_encoded')
print(mapping.to_string())