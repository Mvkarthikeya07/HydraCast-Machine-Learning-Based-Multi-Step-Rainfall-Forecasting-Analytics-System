import numpy as np
import joblib

# ==============================
# LOAD MODEL + SCALER
# ==============================
model = joblib.load("models/rf_model.pkl")
scaler = joblib.load("models/scaler.pkl")

TIME_STEP = 10

# ==============================
# PREDICTION FUNCTION
# ==============================
def predict_rainfall(last_values):
    """
    last_values shape: (10, 3)
    [rainfall, temp, humidity]
    """

    # Convert to numpy
    last_values = np.array(last_values)

    # Scale
    scaled = scaler.transform(last_values)

    # Flatten (RF expects 1D input)
    input_data = scaled.flatten().reshape(1, -1)

    # Predict
    pred = model.predict(input_data)

    # Inverse scale (only rainfall)
    dummy = np.zeros((1, 3))
    dummy[0][0] = pred[0]

    pred_actual = scaler.inverse_transform(dummy)

    return pred_actual[0][0]