import pandas as pd

df = pd.read_csv('data/city_day_cleaned.csv')

print("Available columns:")
print(df.columns.tolist())

cols = ['no', 'nox', 'nh3', 'toluene', 'xylene']
print("\nMean values for imputation:")
print(df[cols].mean().round(4))

print("\nUnique cities (we need to recreate encoding):")
print(sorted(df['city'].unique().tolist()))