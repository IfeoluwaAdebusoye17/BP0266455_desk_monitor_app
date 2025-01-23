from celery import Celery
from frontend.app import DeskStatus, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672/')

@app.task
def save_live_data():
    desks = DeskStatus.query.all()
    data = [{
        'desk_id': desk.id,
        'docking_station_id': desk.docking_station_id,
        'status': desk.status,
        'last_updated': desk.last_updated,
        'temperature': desk.temperature,
        'humidity': desk.humidity,
        'light': desk.light,
        'noise': desk.noise
    } for desk in desks]

    # Connect to the target PostgreSQL database using SQLAlchemy
    database_uri = os.getenv('SQL_DATABASE_URI')
    engine = create_engine(database_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert data into the target table
    for entry in data:
        session.execute("""
            INSERT INTO past_occupancy_ieq (desk_id, docking_station_id, status, last_updated, temperature, humidity, light, noise)
            VALUES (:desk_id, :docking_station_id, :status, :last_updated, :temperature, :humidity, :light, :noise)
        """, entry)

    session.commit()
    session.close()

# Configure periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'save-live-data-every-minute': {
        'task': 'tasks.save_live_data',
        'schedule': crontab(),
    },
}