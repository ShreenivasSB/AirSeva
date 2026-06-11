# 🌫️ AirSeva: Agentic Air Quality Health Advisory System

AirSeva is a 4-agent agentic AI system designed to provide real-time air quality health advisories tailored for Indian communities. By integrating real-time environmental data with machine learning risk prediction and Gemini-powered LLM advisories, AirSeva helps individuals manage their exposure to air pollution based on their personalized health profile.

Developed as part of the **1M1B AI for Sustainability** internship in collaboration with **IBM SkillsBuild + AICTE** at **Dayananda Sagar University, Bangalore**.

---

## 📖 Project Overview

AirSeva operates as an orchestrated multi-agent system that bridges environmental data science with actionable public health insights. It auto-detects or accepts a user's location (from 26 supported Indian cities), queries live pollution and historical weather data, predicts health risk levels using a trained Random Forest model, generates context-aware medical recommendations using Gemini, and compiles standard PDF and text health reports.

---

## ✨ Features

- **4-Agent Pipeline**: Highly modularized agent workflow orchestrated in sequence to fetch data, predict risk, generate advisories, and compile reports.
- **📍 GPS Snapping & Fallback**: Snaps user's GPS coordinates to the nearest supported city or allows selection via search/dropdown.
- **👤 Personal Health Profile**: Dynamic inputs for age, asthma, smoking status, and outdoor work conditions.
- **🧮 Personalized Vulnerability Score (0–8)**: A weighted index highlighting the user's specific susceptibility to air pollution.
- **🤖 Machine Learning Risk Prediction**: Random Forest model predicting health risk level (Low / Moderate / High) with classification confidence.
- **📊 WHO 2021 Guidelines Comparison**: Interactive bar charts comparing live chemical readings against strict WHO 2021 limit standards.
- **📥 Downloadable Reports**: Exports clean summaries as TXT files or formatted PDFs complete with health recommendations.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    UI["🖥️ Streamlit UI\nUser input · city · health profile"]
    ORC["⚙️ Orchestrator\nCoordinates agents · manages pipeline"]
    A1["🌐 Agent 1 · Data Fetcher\nFetches live AQI · weather · pollutant data"]
    A2["🤖 Agent 2 · ML Prediction\nRandom Forest · risk level · confidence score"]
    A3["💬 Agent 3 · Advisory\nGemini 2.5 Flash · personalised health advice"]
    A4["📄 Agent 4 · Report\nGenerates PDF + TXT downloadable report"]
    OUT["📊 Output · Streamlit Dashboard\nAQI charts · risk level · WHO compare · advice"]

    WAQI["WAQI API\nLive AQI data"]
    METEO["Open-Meteo\nWeather data"]
    WHO["WHO 2021\nPollutant limits"]
    SCORE["Score 0–8\nVulnerability index"]
    GEM["Gemini API\ngoogle-genai 2.7"]
    RPT["PDF · TXT\nReport download"]
    ENV[".env config\nWAQI_TOKEN · GEMINI_API_KEY"]

    UI --> ORC --> A1 --> A2 --> A3 --> A4 --> OUT
    WAQI -->|live feed| A1
    METEO -->|weather| A1
    WHO -->|limits| A2
    SCORE -->|output| A2
    GEM -->|LLM call| A3
    A4 -->|export| RPT
    ENV -.->|secrets| A1
    ENV -.->|secrets| A3
```

---

## 🛠️ Tech Stack

- **Core & Logic**: Python 3.10+
- **Frontend / Web App**: Streamlit
- **ML Framework**: scikit-learn 1.8.0 (Random Forest Classifier)
- **Generative AI API**: google-genai 2.7.0 (using `gemini-2.5-flash`)
- **Data APIs**: WAQI API (World Air Quality Index), Open-Meteo Air Quality API
- **Data Processing**: pandas, numpy
- **Visualization**: Plotly, Folium, streamlit-folium
- **PDF Generation**: fpdf2

---

## 📁 Project Folder Structure

```
SRP_PROJECT/
├── agents/                      # Modulized 4-agent logic
│   ├── agent_1_data_fetcher.py  # Fetches live/historical API data and engineers lag features
│   ├── agent_2_ml_prediction.py # Runs Random Forest model prediction
│   ├── agent_3_advisory.py      # Queries Gemini for personalized advice
│   └── agent_4_report.py        # Compiles structured JSON/text reports and checks WHO limits
├── data/                        # Datasets (CPCB India Kaggle data)
│   ├── city_day.csv
│   └── city_day_cleaned.csv
├── models/                      # ML models
│   └── health_risk_rf_model.pkl # Trained Random Forest model file
├── notebooks/                   # Jupyter notebooks for model development & EDA
├── app.py                       # Main Streamlit dashboard application
├── orchestrator.py              # CLI & module execution manager orchestrating all 4 agents
├── requirements.txt             # Project library dependencies
└── .env                         # Local environment configuration file (ignored in Git)
```

---

## 🚀 Setup & Execution Instructions

Follow these steps to set up and run the project locally on your machine:

### 1. Create a Virtual Environment
```bash
python -m venv .venv
```
Activate the environment:
- **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
- **Mac/Linux**: `source .venv/bin/activate`

### 2. Install Project Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Local Environment Variables
Create a file named `.env` in the project root directory:
```env
WAQI_TOKEN=your_waqi_api_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```
* Note: You can obtain a free WAQI token at [aqicn.org/data-platform/token/](https://aqicn.org/data-platform/token/).

### 4. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
The application will launch and be accessible in your web browser at `http://localhost:8501`.

---

## 🤖 The 4-Agent Architecture

AirSeva partitions its logic across 4 distinct autonomous agents:

```
[User Input] ──> [Agent 1: Data Fetcher] ──> [Agent 2: ML Predictor] ──> [Agent 3: Advisor] ──> [Agent 4: Reporter] ──> [Final PDF/TXT]
```

1. **Agent 1: Data Fetcher (`agent_1_data_fetcher.py`)**
   Resolves the requested location into one of the 26 canonical Indian cities. Fetches live pollutant indices ($PM_{2.5}, PM_{10}, NO_2, SO_2, CO, O_3$) from the WAQI API, queries 7-day hourly historical readings from Open-Meteo, and computes rolling average/lag features.
2. **Agent 2: Machine Learning Predictor (`agent_2_ml_prediction.py`)**
   Prepares the 22 engineered features, loads the pre-trained Random Forest model, and predicts the class health risk level (Low, Moderate, High) along with class assignment confidence.
3. **Agent 3: Health Advisor (`agent_3_advisory.py`)**
   Takes the live pollutant concentrations, ML risk level, and user vulnerability details and prompts `gemini-2.5-flash` using structured system instructions to formulate highly tailored, empathetic, and actionable medical/lifestyle advice.
4. **Agent 4: Report Compiler (`agent_4_report.py`)**
   Validates outputs, checks concentration levels against strict WHO 2021 air quality limits, compiles a structured JSON output, and formats raw text summaries alongside PDF export utilities.

---

## 🏙️ Supported Indian Cities (26)

AirSeva tracks and snaps location queries to these 26 major cities:

| | | | |
|---|---|---|---|
| Ahmedabad | Chandigarh | Hyderabad | Patna |
| Aizawl | Chennai | Jaipur | Shillong |
| Amaravati | Coimbatore | Jorapokhar | Talcher |
| Amritsar | Delhi | Kochi | Thiruvananthapuram |
| Bengaluru | Ernakulam | Kolkata | Visakhapatnam |
| Bhopal | Gurugram | Lucknow | |
| Brajrajnagar | Guwahati | Mumbai | |

---

## 📊 WHO 2021 Air Quality Limits

The system compares real-time chemical concentration readings against these strict guidelines:

| Pollutant | WHO 2021 Limit Value | Averaging Time |
|---|---|---|
| **PM2.5** | $15.0 \ \mu g/m^3$ | 24-hour |
| **PM10** | $45.0 \ \mu g/m^3$ | 24-hour |
| **NO2** | $10.0 \ \mu g/m^3$ | Annual |
| **SO2** | $40.0 \ \mu g/m^3$ | 24-hour |
| **CO** | $4.0 \ mg/m^3$ | 8-hour |
| **O3** (Ozone) | $60.0 \ \mu g/m^3$ | 8-hour |

---

## 🧮 Vulnerability Score Guide (0–8)

User vulnerability is evaluated out of a maximum score of 8 based on weighted physiological and lifestyle indicators:

* **Age Profile** (Max 2 pts):
  - Age $< 12$ or $> 60$ years: **+2 points** (sensitive populations)
  - Age $12 - 60$ years: **0 points**
* **Asthma Diagnosis** (Max 3 pts):
  - Diagnosed with Asthma: **+3 points**
* **Smoking Habit** (Max 2 pts):
  - Smoker: **+2 points**
* **Occupational Exposure** (Max 1 pt):
  - Outdoor Worker: **+1 point**

### Vulnerability Level Categories:
- **Score 0 – 1**: **🟢 Low Vulnerability**
- **Score 2 – 4**: **🟡 Moderate Vulnerability**
- **Score 5 – 8**: **🔴 High Vulnerability**

---

## 🎓 Internship & Credentials

This project was built during the MCA internship program:
- **Program**: 1M1B (1 Million 1 Billion) AI for Sustainability
- **Collaborating Partners**: IBM SkillsBuild & AICTE (All India Council for Technical Education)
- **Institution**: Dayananda Sagar University (DSU), Bangalore
- **Developer**: Shreenivas S B
- **Completion Date**: June 2026
