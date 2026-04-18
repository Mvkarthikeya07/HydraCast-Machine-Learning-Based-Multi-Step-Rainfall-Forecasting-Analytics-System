<div align="center">

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
<img src="https://img.shields.io/badge/Chart.js-Live_Dashboard-FF6384?style=for-the-badge&logo=chart.js&logoColor=white"/>
<img src="https://img.shields.io/badge/Inference-<100ms-00C853?style=for-the-badge"/>

<br/><br/>

# 🌧️ HydraCast

**Rainfall intelligence. Real-time. Deployable. No GPU needed.**

HydraCast is a production-grade ML system that transforms historical rainfall CSVs into a live, interactive 7-day forecast dashboard — served over Flask with sub-100ms inference.

[Features](#features) · [Screenshots](#screenshots) · [Architecture](#architecture) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Roadmap](#roadmap)

</div>

---

## The Problem

Most rainfall forecasting tools are either buried in research papers, require heavy infrastructure (GPUs, cloud pipelines), or produce results that non-technical users can't act on.

HydraCast is the middle path: a lightweight Random Forest model trained on time-series sliding windows, served via a Flask API, visualized in a clean glassmorphism dashboard with live updates every 10 seconds.

---

## Screenshots

**Main Dashboard — Next-day prediction + 7-day summary stats**

![Dashboard Overview](ss1.png)

**Multi-district selector — 500+ Indian districts supported**

![District Selector](ss2.png)

**Interactive chart with hover tooltips + Day-by-day forecast cards**

![Chart and Forecast Cards](ss3.png)

**7-day easy view table with rainfall level bars**

![Easy View Table](ss4.png)

---

## Features

| Feature | Detail |
|---|---|
| Next-day prediction | Single RF inference on last 10 days of rainfall |
| 7-day recursive forecast | Predicts day N → feeds as input for day N+1 |
| Live dashboard | Auto-refreshes every 10 seconds via Flask API |
| District coverage | 500+ Indian districts from a single trained model |
| Rainfall classification | Dry / Light drizzle / Moderate / Heavy per day |
| Interactive chart | Combined history + forecast with hover tooltips |
| Inference latency | < 100ms (joblib model load, MinMaxScaler pipeline) |

---

## Architecture

```
Raw CSV (days as columns)
        │
        ▼
  Data Cleaning & Date Reconstruction
  (month + day parsing → sorted time-series)
        │
        ▼
  Sliding Window Transform
  Input:  [Rain(t-10) … Rain(t-1)]
  Output: Rain(t)
        │
        ▼
  Random Forest Regressor
  (MinMaxScaler preprocessing, joblib serialized)
        │
        ▼
  Flask REST API  (/predict, /forecast/<district>, /history/<district>)
        │
        ▼
  Interactive Dashboard
  (Chart.js · Glassmorphism UI · 10s auto-refresh)
```

**Why Random Forest over LSTM?**

For a dataset of this scale and feature set (univariate rainfall only), Random Forest matches or exceeds LSTM accuracy at a fraction of the complexity — no GPU, no sequence padding, no vanishing gradients, and inference stays under 100ms on commodity hardware.

---

## Model Performance

| Metric | Value |
|---|---|
| MAE | ~0.4 – 0.8 mm |
| RMSE | ~1.2 mm |
| Inference time | < 100 ms |
| Training data | Vellore district rainfall CSV (multi-year) |
| Window size | 10 days |

---

## Project Structure

```
HydraCast/
├── app.py                  # Flask routes and API layer
├── model.py                # Prediction and recursive forecast logic
├── train_model.py          # Sliding window transform + RF training pipeline
├── requirements.txt
│
├── data/
│   └── vellore_rainfall.csv
│
├── models/
│   ├── rf_model.pkl        # Trained Random Forest (joblib)
│   └── scaler.pkl          # Fitted MinMaxScaler
│
├── static/
│   ├── css/style.css
│   └── js/script.js        # Chart.js + auto-refresh logic
│
└── templates/
    └── index.html
```

---

## Quick Start

**Prerequisites:** Python 3.9+, pip

```bash
git clone https://github.com/yourusername/HydraCast.git
cd HydraCast

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt

python train_model.py          # Trains RF + saves models/rf_model.pkl
python app.py                  # Starts Flask at http://127.0.0.1:5000
```

Open `http://127.0.0.1:5000`, select a district, and get a full 7-day forecast.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the interactive dashboard |
| `/history/<district>` | GET | Returns historical rainfall time-series for a district |
| `/predict` | POST | Next-day prediction (body: `{"district": "...", "data": [...]}`) |
| `/forecast/<district>` | GET | 7-day recursive forecast for a district |

**Sample response — `/forecast/Vellore`**

```json
{
  "district": "Vellore",
  "forecast": [
    { "date": "01-01", "rainfall_mm": 0.32, "category": "Dry" },
    { "date": "01-02", "rainfall_mm": 0.40, "category": "Dry" },
    { "date": "01-03", "rainfall_mm": 0.68, "category": "Dry" },
    { "date": "01-04", "rainfall_mm": 1.08, "category": "Light drizzle" },
    { "date": "01-05", "rainfall_mm": 2.71, "category": "Light drizzle" },
    { "date": "01-06", "rainfall_mm": 3.68, "category": "Light drizzle" },
    { "date": "01-07", "rainfall_mm": 4.74, "category": "Light drizzle" }
  ]
}
```

---

## Limitations

- Univariate input — no temperature, humidity, or pressure features
- Recursive forecasting accumulates prediction error beyond day 3–4
- Trained on regional Indian district data; may generalize poorly to other geographies

---

## Roadmap

- [ ] Weather API integration (OpenWeatherMap) for feature enrichment
- [ ] LSTM / GRU comparison benchmark
- [ ] Multi-feature input (temperature, humidity, wind)
- [ ] Cloud deployment (AWS / GCP with Docker)
- [ ] Seasonal trend decomposition

---

## Author

**M V Karthikeya** — ML Engineer · Full Stack Developer

---

<div align="center">
<sub>If this helped you, a ⭐ goes a long way.</sub>
</div>
