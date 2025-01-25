from flask import Flask, jsonify, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load models

# Load models
regression_model = joblib.load('regression_model.pkl')  # IEQ prediction
classification_model = joblib.load('classification_model.pkl')  # Occupancy prediction


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input data as JSON
        data = request.json  # Expecting Zone, Desk, Hour, DayOfWeek, DayOfMonth
        
        # Convert input data into a DataFrame
        input_df = pd.DataFrame([data])
        
        # Predict occupancy
        occupied_prediction = classification_model.predict(input_df)[0]
        
        # Predict IEQ factors
        ieq_prediction = regression_model.predict(input_df)[0]
        
        # Combine results into a response
        response = {
            'Occupied': int(occupied_prediction),
            'Temperature': ieq_prediction[0],
            'Humidity': ieq_prediction[1],
            'Light': ieq_prediction[2],
            'Noise': ieq_prediction[3]
        }
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)})


from datetime import datetime, timedelta
import pandas as pd

def generate_future_inputs():
    future_time = datetime.now() + timedelta(hours=1)  # Predict for the next hour
    return {
        'Zone': 1,  # Example zone
        'Desk': 5,  # Example desk
        'Hour': future_time.hour,
        'DayOfWeek': future_time.weekday(),
        'DayOfMonth': future_time.day
    }
