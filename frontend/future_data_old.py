from flask import Flask, jsonify, request
import joblib
import pandas as pd
from datetime import date, timedelta

app = Flask(__name__)

# Load models
regression_model = joblib.load('regression_model.pkl')  # IEQ prediction
classification_model = joblib.load('classification_model.pkl')  # Occupancy prediction


def future_columns():
    today_date = date.today()

    data_rows = []

    #Step generate the columns data for 1 month ahead from the date today. Starting from 8 am to 7pm from zone 1 - 5 in the office from desk 1 - 10

    #This is just a proof of concept the real loop should also increment from 8am to 7pm
    for i in range(len(28)):
        #Extra for loop that will go from the time of 8am to 7pm in increment of 1 hour. E.G will remain on the date at 7am when all zones and desks have been processed in the loop will then go to 8am
        for j in range(len(5)):
            for x in range(len(10)):
                rows_dict = {row_date : today_date + timedelta(days=1), row_zone: j, row_desk: x}
                data_rows.append(row_dict)

    future_rows = []
    #Feed these columns into the model
    for data_entries in data_rows:
        ieq_prediction = regression_model(data_entries)
        occupancy_prediction = classification(data_entries)
        predicted_data = ieq_prediction + occupancy_prediction
        future_rows.append(predicted_data)



#Get the data and feed into the database
target_database_uri = os.getenv('SQL_DATABASE_URI')


target_engine = create_engine(target_database_uri)


TargetSession = sessionmaker(bind = target_engine)

def save_live_data():
    print("Starting the predicted_data task...")

    #Step 2: Transform to a dictionary for insertion
    data = [
        {
            'id': 1 # Will need to add auto increment feature as is primary key
            'timestamp': data.timestamp,
            'zone': data.zone,
            'desk': data.desk,
            'occupied': data.occupied,
            'temperature': data.temperature,
            'humidity': data.humidity,
            'light': data.light,
            'noise': data.noise,
        }
        for data in future_rows
    ]
    #Step 3: Insert data into the target database
    target_session = TargetSession()

    try:
        target_session.execute(
            text("""
                INSERT INTO future_data (id, timestamp, zone, desk, occupied, temperature, humidity, light, noise)
                VALUES (:id, :timestamp, :zone, :desk, :occupied, :temperature, :humidity, :light, :noise)
            """),
            data
        )
        target_session.commit()
        print(f"Inserted {len(data)} records successfully!")
    except Exception as e:
        target_session.rollback()
        print(f"Error saving data: {e}")
    finally:
        target_session.close()








#The database should be hooked up to the front end so that it can be displayed




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

