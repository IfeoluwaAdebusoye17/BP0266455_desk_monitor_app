from flask import Flask, render_template
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_socketio import SocketIO, emit #For real-time updates
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

import os
from dotenv import load_dotenv
load_dotenv() # Take environmental variables from .env
database_uri = os.getenv('SQL_DATABASE_URI')



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




app = Flask(__name__)

#Configure the PostgreSQL database connection
app.config[ 'SQLALCHEMY_DATABASE_URI' ] = database_uri
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS' ] = False

db = SQLAlchemy(app)
socketio = SocketIO(app) #Set up real-time communication

#Define models for your database
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    laptop_id = db.Column(db.String(50), nullable=False, unique=True)

class DockingStation(db.Model):
    __tablename__ = 'docking_stations'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), nullable=False, unique=True)
    desk_number = db.Column(db.String(10), nullable=False)

class DeskStatus(db.Model):
    __tablename__ = 'desk_status'
    id = db.Column(db.Integer, primary_key=True)
    docking_station_id = db.Column(db.Integer, db.ForeignKey('docking_stations.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    status = db.Column(db.String(20), default='free')
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    light = db.Column(db.Numeric(6, 2))
    noise = db.Column(db.Numeric(5, 2))

# Home route to render the desk usage page
@app.route('/')
def home():
    return render_template('index.html')

'''
@app.route('/index1')
def index1():
    return render_template('index1.html')
'''

#API endpoint to get desk statuses
@app.route('/desks', methods=['GET'])
def get_desk_status():
    desks = DeskStatus.query.all()
    return jsonify([{
        'desk_id': desk.id,
        'docking_station_id': desk.docking_station_id,
        'status': desk.status,
        'last_updated': desk.last_updated,
        'temperature': desk.temperature,
        'humidity': desk.humidity,
        'light': desk.light,
        'noise': desk.noise
    } for desk in desks])

#API endpoint to update desk status (when a laptop is connected)
@app.route('/desks/<int:docking_station_id>', methods=['PUT'])
def update_desk_status(docking_station_id):
    data = request.get_json()
    employee_id = data.get('employee_id')  # This could be None when unoccupied
    desk = DeskStatus.query.filter_by(docking_station_id=docking_station_id).first()

    if desk:
        # Update desk status based on whether employee_id is provided or not
        if employee_id is not None:
            desk.employee_id = employee_id
            desk.status = 'occupied'
        else:
            desk.employee_id = None
            desk.status = 'free'  # Mark as free when unoccupied
        db.session.commit()
        socketio.emit('desk_update', {'desk_id': desk.id, 'status': desk.status}, broadcast=True)
        return jsonify({'message': 'Desk status updated'}), 200
    
    return jsonify({'message': 'Docking station not found'}), 404

#Database connection
engine = create_engine(database_uri)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the database model
class PastOccupancyIEQ(Base):
    __tablename__ = 'past_occupancy_ieq'
    id = Column(Integer, primary_key=True)
    desk_id = Column(Integer)
    docking_station_id = Column(Integer)
    status = Column(String)
    last_updated = Column(DateTime)
    temperature = Column(Float)
    humidity = Column(Float)
    light = Column(Float)
    noise = Column(Float)

# Route to display data
@app.route("/index1")
def index1():
    session = Session()
    records = session.query(PastOccupancyIEQ).all()
    session.close()

    # Pass data to the template
    return render_template("index1.html", records=records)







#Database connection
#database_uri = 'postgresql://postgres:Postgrestill100k$@localhost/office_management'
#engine = create_engine(database_uri)
#Session = sessionmaker(bind=engine)
#Base = sqlalchemy.orm.declarative_base()

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
@app.route("/index2")
def index2():
    session = Session()
    records = session.query(FutureOccupancyIEQ).all()
    session.close()

    # Pass data to the template
    return render_template("index2.html", records=records)

if __name__ == '__main__':
    # Ensure the app context is set up
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    socketio.run(app)