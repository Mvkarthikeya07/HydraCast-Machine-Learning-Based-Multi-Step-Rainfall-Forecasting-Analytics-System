from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from model import predict_rainfall

app = Flask(__name__)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv('data/vellore_rainfall.csv', sep=';')
df.columns = df.columns.str.strip().str.lower()

# ==============================
# GET DISTRICTS
# ==============================
districts = sorted(df['district'].dropna().unique())

# ==============================
# PROCESS DISTRICT DATA
# ==============================
def process_district(district):
    d = df[df['district'].str.lower() == district.lower()]

    if d.empty:
        return None

    day_cols = [col for col in df.columns if any(x in col for x in ['st','nd','rd','th'])]

    d = d.melt(
        id_vars=['district', 'month'],
        value_vars=day_cols,
        var_name='day',
        value_name='rainfall'
    )

    d['day'] = d['day'].str.extract(r'(\d+)')
    d['day'] = pd.to_numeric(d['day'], errors='coerce')

    # Month parsing
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

    d['date'] = pd.to_datetime(
        dict(year=2020, month=d['month_num'], day=d['day']),
        errors='coerce'
    )

    d = d.dropna(subset=['date'])

    d['rainfall'] = pd.to_numeric(d['rainfall'], errors='coerce').fillna(0)

    d = d.sort_values('date')

    return d[['date', 'rainfall']]

# ==============================
# ROUTES
# ==============================

@app.route('/')
def home():
    return render_template('index.html', districts=districts)


@app.route('/history/<district>')
def history(district):
    d = process_district(district)

    if d is None:
        return jsonify({"dates": [], "rainfall": []})

    return jsonify({
        "dates": d['date'].dt.strftime('%m-%d').tolist(),
        "rainfall": d['rainfall'].tolist()
    })


@app.route('/predict', methods=['POST'])
def predict():
    district = request.json['district']

    d = process_district(district)

    if d is None or len(d) < 10:
        return jsonify({"prediction": 0})

    rainfall = d['rainfall'].values[-10:]

    last_values = rainfall.reshape(-1, 1)

    prediction = predict_rainfall(last_values)

    return jsonify({
        "prediction": round(float(prediction), 2)
    })


# ==============================
# 🔥 FORECAST ROUTE (NEW)
# ==============================
@app.route('/forecast/<district>')
def forecast(district):
    d = process_district(district)

    if d is None or len(d) < 10:
        return jsonify({"dates": [], "rainfall": []})

    rainfall = d['rainfall'].values[-10:]

    input_seq = rainfall.reshape(-1, 1)

    future_preds = []
    future_dates = []

    last_date = d['date'].iloc[-1]

    for i in range(7):
        pred = predict_rainfall(input_seq)

        future_preds.append(round(float(pred), 2))
        future_dates.append((last_date + pd.Timedelta(days=i+1)).strftime('%m-%d'))

        new_row = [pred]
        input_seq = np.vstack([input_seq[1:], new_row])

    return jsonify({
        "dates": future_dates,
        "rainfall": future_preds
    })


# ==============================
# RUN
# ==============================
if __name__ == '__main__':
    app.run(debug=True)