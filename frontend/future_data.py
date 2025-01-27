from flask import Flask
import joblib
import pandas as pd
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
import sqlalchemy
from flask import render_template

# Initialize Flask App
app = Flask(__name__)

'''
# Load models
regression_model = joblib.load('regression_model.pkl')  # IEQ prediction model
classification_model = joblib.load('classification_model.pkl')  # Occupancy prediction model

# Generate future columns for a month
def generate_future_data():
    today_date = datetime.now()
    data_rows = []

    # Loop for one month of data
    for day in range(30):  # 30 days in a month
        current_date = today_date + timedelta(days=day)
        for hour in range(8, 20):  # Office hours: 8AM to 7PM
            for zone in range(1, 6):  # Zones 1 to 5
                for desk in range(1, 11):  # Desks 1 to 10
                    data_rows.append({
                        'Zone': zone,
                        'Desk': desk,
                        'Hour': hour,
                        'DayOfWeek': current_date.weekday(),
                        'DayOfMonth': current_date.day,
                    })
    return pd.DataFrame(data_rows)


def predict_future_data(data_rows):
    # Prepare input features for the models
    input_features = data_rows[['Zone', 'Desk', 'Hour', 'DayOfWeek', 'DayOfMonth']]

    # Batch predictions
    occupancy_predictions = classification_model.predict(input_features)
    ieq_predictions = regression_model.predict(input_features)

    # Combine predictions with input data
    data_rows['Occupied'] = occupancy_predictions
    data_rows['Predicted_Temperature'] = ieq_predictions[:, 0]
    data_rows['Predicted_Humidity'] = ieq_predictions[:, 1]
    data_rows['Predicted_Light'] = ieq_predictions[:, 2]
    data_rows['Predicted_Noise'] = ieq_predictions[:, 3]

    return data_rows


#print(predicted_data_test)


# Save predicted data to the database
def save_to_database(predicted_data):
    # Database connection
    target_database_uri = 'postgresql://postgres:Postgrestill100k$@localhost/office_management'

    engine = create_engine(target_database_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert data into database
    try:
        predicted_data.to_sql('predicted_data', con=engine, if_exists='append', index=False)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving data to the database: {e}")
    finally:
        session.close()

future_data_test = generate_future_data()

predicted_data_test = predict_future_data(future_data_test)

print(save_to_database(predicted_data_test))

@app.route('/generate-predictions', methods=['GET'])
def generate_predictions():
    try:
        # Step 1: Generate future data
        future_data = generate_future_data()

        # Step 2: Predict future data
        predicted_data = predict_future_data(future_data)

        # Step 3: Save predicted data to the database
        save_to_database(predicted_data)

        return {"status": "success", "message": "Predicted data saved successfully."}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


'''

#Database connection
database_uri = 'postgresql://postgres:Postgrestill100k$@localhost/office_management'
engine = create_engine(database_uri)
Session = sessionmaker(bind=engine)
Base = sqlalchemy.orm.declarative_base()

# Define the database model
class FutureOccupancyIEQ(Base):
    __tablename__ = 'predicted_data'
    id = Column(Integer, primary_key=True)
    Zone = Column(Integer)
    Desk = Column(Integer)
    Hour = Column(Integer)
    DayOfWeek = Column(Integer)
    DayOfMonth = Column(Integer)
    Occupied = Column(Integer)
    Predicted_Temperature = Column(Float)
    Predicted_Humidity = Column(Float)
    Predicted_Light = Column(Float)
    Predicted_Noise = Column(Float)


# Route to display data
@app.route("/")
def home():
    session = Session()
    records = session.query(FutureOccupancyIEQ).all()
    session.close()

    # Pass data to the template
    return render_template("index2.html", records=records)


if __name__ == '__main__':
    # Ensure the database tables exist
    app.run(port=5001)
