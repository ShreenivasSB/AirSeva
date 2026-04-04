# 🌫️ Air Quality Health Risk Prediction System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange?logo=scikit-learn&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Model Accuracy](https://img.shields.io/badge/Model%20Accuracy-87.8%25-brightgreen)
![Status](https://img.shields.io/badge/Status-Live-success)

> **Real-time air quality monitoring and personal health risk prediction powered by Machine Learning.**

---

## 📖 Overview

The **Air Quality Health Risk Prediction System** is an end-to-end interactive web application that fetches live AQI (Air Quality Index) data for any location in India, analyses pollutant concentrations, and predicts the personal health risk level (Low / Moderate / High) using a trained Random Forest classifier. The app factors in the user's personal health profile — age, pre-existing conditions, and physical activity — to compute a personalised vulnerability score and generate a downloadable health report. Built as an MCA final-year portfolio project, this system bridges environmental data science with actionable public health insights.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📍 GPS Auto-Detection | Detects user's location via browser GPS (streamlit-js-eval) |
| 🔁 3-Layer Location Fallback | GPS → City name search → Manual coordinate entry |
| 👤 Personal Health Profile | Collects age group, medical conditions, and activity level |
| 🧮 Vulnerability Score (0–8) | Weighted score based on health risk factors |
| 🤖 ML Risk Prediction | Random Forest model with confidence % for Low/Moderate/High risk |
| 📊 WHO 2021 Limits Chart | Plotly bar chart comparing live pollutants against WHO guidelines |
| 📅 3-Day Health Risk Forecast | Forward-projected risk based on current AQI trend |
| 📥 Downloadable .txt Report | Full health report with AQI, pollutants, risk, and recommendations |
| 📈 AQI Session History Chart | Plotly line chart tracking AQI readings across the session |
| ⚡ API Response Caching | WAQI API responses cached to reduce redundant calls |

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **Frontend / UI** | Streamlit 1.35 |
| **ML Model** | scikit-learn (Random Forest Classifier) |
| **Data Manipulation** | Pandas, NumPy |
| **Visualisation** | Plotly, Folium, streamlit-folium |
| **Live AQI Data** | WAQI API (World Air Quality Index) |
| **Geocoding** | OpenStreetMap Nominatim |
| **GPS Detection** | streamlit-js-eval |
| **Environment Config** | python-dotenv |
| **Model Serialisation** | joblib |
| **Dataset** | CPCB India (Kaggle) |

---

## 🤖 ML Model Details

| Parameter | Value |
|---|---|
| **Algorithm** | Random Forest Classifier |
| **Accuracy** | **87.8%** |
| **Weighted F1-Score** | 0.88 |
| **F1 — High Risk** | 0.91 |
| **F1 — Low Risk** | 0.90 |
| **F1 — Moderate Risk** | 0.83 |
| **Features Used** | 22 (AQI sub-indices, pollutant concentrations, engineered features) |
| **Train/Test Split** | 80 / 20 |
| **Random State** | 42 |
| **Data Leakage** | ❌ None — AQI Bucket column excluded from features |
| **Validation** | Stratified split; no future data used |

---

## 📁 Project Structure

```
SRP_PROJECT/
├── app/
│   └── app.py                   # Main Streamlit application
├── data/
│   ├── city_day.csv             # Raw CPCB dataset
│   └── city_day_cleaned.csv     # Cleaned dataset used for training
├── models/
│   └── health_risk_rf_model.pkl # Trained Random Forest model
├── notebooks/
│   ├── 01_data_prep.ipynb       # Data cleaning and preprocessing
│   ├── 02_eda.ipynb             # Exploratory Data Analysis
│   └── 03_feature_engineering.ipynb  # Feature engineering and model training
├── reports/
│   └── monthly_median_aqi.csv   # Monthly AQI summary report
├── .env                         # Local environment variables (NOT pushed to GitHub)
├── .gitignore
└── requirements.txt
```

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/air-quality-health-risk.git
cd air-quality-health-risk
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```env
WAQI_TOKEN=your_waqi_api_token_here
```
> Get your free API token at [https://aqicn.org/data-platform/token/](https://aqicn.org/data-platform/token/)

### 4. Run the app
```bash
streamlit run app/app.py
```

The app will open at `http://localhost:8501`

---

## 📦 Dataset

| Property | Details |
|---|---|
| **Source** | Central Pollution Control Board (CPCB), India |
| **Platform** | [Kaggle — Air Quality Data in India](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) |
| **Time Period** | 2015 – 2020 |
| **Records** | 29,531 rows |
| **Cities Covered** | 26 major Indian cities |
| **Key Columns** | City, Date, PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, AQI, AQI_Bucket |

---

## 🖼️ Screenshots

> _Screenshots will be added after Streamlit Cloud deployment._

| View | Description |
|---|---|
| 📍 Location Detection | GPS / city search UI |
| 👤 Health Profile Form | Vulnerability score calculator |
| 📊 AQI Dashboard | Live pollutant readings + WHO limits chart |
| 📥 Downloadable Report | Sample .txt health report |

---

## 🌐 Live Demo

> 🔗 **[Live App on Streamlit Cloud](#)** ← _Link will be updated after deployment_

---

## 👨‍💻 Author

**Shreenivas S B**  
MCA Student — Dayananda Sagar University, Bangalore  
Graduating: June 2026  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/YOUR_LINKEDIN)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/YOUR_USERNAME)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

> *Built with ❤️ as a Data Analytics portfolio project — combining real-world environmental data, machine learning, and interactive visualisation.*
