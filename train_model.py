import numpy as np
import pandas as pd
import os
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

# ==============================
# CONFIG
# ==============================
RAIN_DATA = "data/vellore_rainfall.csv"

MODEL_PATH = "models/rf_model.pkl"
SCALER_PATH = "models/scaler.pkl"

TIME_STEP = 10

# ==============================
# LOAD DATA
# ==============================
print("📥 Loading datasets...")

rain_df = pd.read_csv(RAIN_DATA, sep=';')

rain_df.columns = rain_df.columns.str.strip().str.lower()

# ==============================
# PROCESS RAINFALL
# ==============================
def process_rainfall(df):
    day_cols = [col for col in df.columns if any(x in col for x in ['st','nd','rd','th'])]

    d = df.melt(
        id_vars=['district', 'month'],
        value_vars=day_cols,
        var_name='day',
        value_name='rainfall'
    )

    # Extract day number
    d['day'] = d['day'].str.extract(r'(\d+)')
    d['day'] = pd.to_numeric(d['day'], errors='coerce')

    # Extract month
    d['month_str'] = d['month'].astype(str).str.lower()

    d['month_num'] = pd.to_numeric(
        d['month_str'].str.extract(r'(\d+)')[0],
        errors='coerce'
    )

    month_map = {
        'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
        'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12
    }

    d['month_num'] = d['month_num'].fillna(
        d['month_str'].str[:3].map(month_map)
    )

    # Create date
    d['date'] = pd.to_datetime(
        dict(year=2020, month=d['month_num'], day=d['day']),
        errors='coerce'
    )

    d = d.dropna(subset=['date'])

    d['rainfall'] = pd.to_numeric(d['rainfall'], errors='coerce').fillna(0)

    print("Rain processed:", len(d))

    return d[['date', 'rainfall']]

rain_processed = process_rainfall(rain_df)

# ==============================
# PREPARE DATA
# ==============================
df = rain_processed.copy()

print("Merged size BEFORE:", len(df))

# ==============================
# 🔥 SPEED OPTIMIZATION
# ==============================
df = df.sample(n=20000, random_state=42)

print("Merged size AFTER sampling:", len(df))

if len(df) < 50:
    raise Exception("❌ Not enough data after merge")

# ==============================
# PREPARE DATA
# ==============================
df = df.sort_values('date')

features = df[['rainfall']].values

scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)

# ==============================
# CREATE SEQUENCES
# ==============================
X, y = [], []

for i in range(len(features_scaled) - TIME_STEP):
    X.append(features_scaled[i:i+TIME_STEP].flatten())
    y.append(features_scaled[i+TIME_STEP][0])

X = np.array(X)
y = np.array(y)

print("Total sequences:", len(X))

# ==============================
# TRAIN RANDOM FOREST (FAST)
# ==============================
print("🚀 Training Random Forest...")

model = RandomForestRegressor(
    n_estimators=50,
    max_depth=8,
    n_jobs=-1,
    random_state=42
)

model.fit(X, y)

# ==============================
# SAVE MODEL
# ==============================
os.makedirs("models", exist_ok=True)

joblib.dump(model, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)

print("✅ Fast model trained successfully!")

# ==============================
# TEST
# ==============================
sample = X[0].reshape(1, -1)
pred = model.predict(sample)

print(f"Sample Prediction (scaled): {pred[0]:.4f}")