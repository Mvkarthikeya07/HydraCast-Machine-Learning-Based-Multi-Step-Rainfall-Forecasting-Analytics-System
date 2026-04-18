<div align="center">

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-REST_API-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
<img src="https://img.shields.io/badge/Chart.js-Glassmorphism_UI-FF6384?style=for-the-badge&logo=chart.js&logoColor=white"/>
<img src="https://img.shields.io/badge/Inference-<100ms-00C853?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge"/>

<br/><br/>

# 🌧️ HydraCast

**District-level rainfall forecasting. Lightweight ML. Live dashboard. No GPU.**

HydraCast takes historical rainfall CSVs, trains a Random Forest on sliding-window sequences, and serves next-day predictions + 7-day recursive forecasts through a Flask API — visualized in a glassmorphism dashboard that auto-refreshes every 10 seconds.

[Screenshots](#screenshots) · [How It Works](#how-it-works) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Design Decisions](#design-decisions) · [Roadmap](#roadmap)

</div>

---

## Screenshots

**Hero dashboard — next-day prediction + 7-day cumulative stats**

![Dashboard](ss1.png)

**500+ Indian districts supported via a single dropdown**

![District Selector](ss2.png)

**Combined history + forecast chart with hover tooltips**

![Chart and Forecast Cards](ss3.png)

**7-day easy-view table with rainfall level badges and proportional level bars**

![Easy View Table](ss4.png)

---

## How It Works

### 1. Data Processing

The raw CSV stores rainfall with days as ordinal columns (`1st`, `2nd`, ... `31st`) and months as text. Both `app.py` and `train_model.py` use `.melt()` to unpivot this into a flat `(date, rainfall)` time-series, with regex-based day extraction and a dual-strategy month parser that handles both numeric and abbreviated month names (`jan`, `feb`, etc.).

### 2. Sliding Window Training

`train_model.py` samples 20,000 rows for training speed, then builds supervised sequences:

```
Input:  [Rain(t-1), Rain(t-2), ..., Rain(t-10)]   → flattened shape (10,)
Output: Rain(t)
```

The MinMaxScaler fits on this univariate rainfall array. Sequences are flattened before being passed to the Random Forest (RF expects 2D input, not 3D).

### 3. Model

```python
RandomForestRegressor(n_estimators=50, max_depth=8, n_jobs=-1, random_state=42)
```

50 trees at depth 8 keeps inference well under 100ms while capturing non-linear rainfall patterns. No GPU, no CUDA, no Docker — just joblib-serialized `.pkl` files loaded once at Flask startup.

### 4. Recursive 7-Day Forecast

`/forecast/<district>` runs a predict-then-slide loop — a single trained model drives all 7 steps:

```python
for i in range(7):
    pred = predict_rainfall(input_seq)
    input_seq = np.vstack([input_seq[1:], [pred]])  # slide window forward
```

### 5. Dashboard

The frontend fires three parallel `fetch()` calls on every load — `/history`, `/forecast`, and `/predict` — then renders a Chart.js line chart, 7 day-cards, and a forecast table with rainfall classification badges. A `setInterval(loadData, 10000)` drives live updates.

Rainfall thresholds used across the UI:

| Label | Range |
|---|---|
| ☀️ Dry | < 1 mm |
| 🌦️ Light drizzle | 1 – 5 mm |
| 🌧️ Moderate rain | 5 – 15 mm |
| ⛈️ Heavy rain | ≥ 15 mm |

---

## Project Structure

```
HydraCast/
├── app.py                   # Flask routes: /, /history, /predict, /forecast
├── model.py                 # predict_rainfall() — scale → flatten → infer → inverse scale
├── train_model.py           # Data pipeline + RF training + joblib serialization
├── requirements.txt
│
├── data/
│   └── vellore_rainfall.csv         # Semicolon-delimited; days as ordinal columns
│
├── models/
│   ├── rf_model.pkl                 # Trained RandomForestRegressor
│   └── scaler.pkl                   # Fitted MinMaxScaler (univariate: rainfall only)
│
├── static/
│   ├── css/style.css                # Glassmorphism, Poppins + DM Mono, responsive grid
│   └── js/script.js                 # Parallel fetch, Chart.js render, 10s auto-refresh
│
└── templates/
    └── index.html                   # Jinja2; district list injected server-side at render
```

---

## Quick Start

**Requirements:** Python 3.9+

```bash
git clone https://github.com/yourusername/HydraCast.git
cd HydraCast

python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Train the model — writes models/rf_model.pkl and models/scaler.pkl
python train_model.py

# Start the server
python app.py
```

Open `http://127.0.0.1:5000`, select a district, and the full forecast loads immediately.

> **Note:** `train_model.py` samples 20,000 rows by default for fast training. To use the full dataset, remove the `.sample(n=20000, random_state=42)` line in `train_model.py`.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Renders the dashboard (Jinja2; districts injected server-side) |
| `/history/<district>` | GET | Full historical `(date, rainfall)` series for a district |
| `/predict` | POST | Next-day prediction from the last 10 days of district data |
| `/forecast/<district>` | GET | 7-day recursive forecast |

**POST `/predict`**
```json
// Request
{ "district": "Vellore" }

// Response
{ "prediction": 0.82 }
```

**GET `/forecast/Vellore`**
```json
{
  "dates":    ["01-01", "01-02", "01-03", "01-04", "01-05", "01-06", "01-07"],
  "rainfall": [0.32,    0.40,    0.68,    1.08,    2.71,    3.68,    4.74]
}
```

---

## Design Decisions

**Random Forest over LSTM** — The dataset is univariate (rainfall only) and regional in scope. At this scale, RF matches LSTM accuracy without sequence padding, GPU dependency, or training instability. Inference stays under 100ms via joblib.

**Window size of 10 days** — Captures the weekly rainfall cycle and short-term monsoon carry-over without overfitting to longer-range seasonal noise.

**One model for all 7 forecast steps** — Rather than training 7 separate horizon-specific models, a single RF is reused recursively. This keeps the system lean and avoids multi-output regression complexity.

**`Promise.all` for parallel API calls** — The frontend fires all three requests simultaneously, so the dashboard loads in one round-trip instead of three sequential fetches.

**Server-side district injection** — The district list is passed into Jinja2 at render time, so no extra API call is needed to populate the dropdown on page load.

---

## Limitations

- Univariate input only — temperature, humidity, and wind are not currently used
- Recursive forecasting accumulates error; day 5–7 predictions are less reliable than day 1–2
- Date reconstruction uses a fixed year (2020), so multi-year trend modeling is not supported in the current pipeline
- `model.py` docstring references a `(10, 3)` input shape (rainfall + temp + humidity), but the actual scaler and training are univariate `(10, 1)` — these should be kept in sync if features are added later

---

## Roadmap

- [ ] Weather API integration (OpenWeatherMap / IMD) for real-time feature enrichment
- [ ] Multi-feature input — temperature, humidity, wind speed
- [ ] LSTM / GRU benchmark against current RF baseline
- [ ] Fix year handling in date reconstruction to support multi-year datasets
- [ ] Docker + cloud deployment (AWS / GCP)
- [ ] Align `model.py` docstring with actual univariate input shape

---

## Requirements

```
flask
pandas
numpy
scikit-learn
joblib
matplotlib
```

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
<sub>Built by M V Karthikeya · If this helped, a ⭐ goes a long way</sub>
</div>
