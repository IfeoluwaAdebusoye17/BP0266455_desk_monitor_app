from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database connection
DATABASE_URI = os.getenv("SQL_DATABASE_URI")
engine = create_engine(DATABASE_URI)
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
@app.route("/")
def display_data():
    session = Session()
    records = session.query(PastOccupancyIEQ).all()
    session.close()

    # Pass data to the template
    return render_template("index1.html", records=records)

if __name__ == "__main__":
    app.run(debug=True, port = 5001)
