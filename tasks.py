import time
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from frontend.app import DeskStatus, db
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env


#from celery import Celery
#from frontend.app import DeskStatus, db

#app = Celery('tasks', broker='amqp://guest:guest@localhost:5672/')

source_database_uri = os.getenv('SQL_DATABASE_URI')
target_database_uri = os.getenv('SQL_DATABASE_URI')

source_engine = create_engine(source_database_uri)
target_engine = create_engine(target_database_uri)

SourceSession = sessionmaker(bind = source_engine)
TargetSession = sessionmaker(bind = target_engine)

def save_live_data():
    print("Starting the save_live_data task...")

    #Step 1: Fetch data from the source database
    source_session = SourceSession()
    desks = source_session.query(DeskStatus).all()
    source_session.close()

    #Step 2: Transform to a dictionary for insertion
    data = [
        {
            'desk_id': desk.id,
            'docking_station_id': desk.docking_station_id,
            'status': desk.status,
            'last_updated': desk.last_updated,
            'temperature': desk.temperature,
            'humidity': desk.humidity,
            'light': desk.light,
            'noise': desk.noise,
        }
        for desk in desks
    ]
    #Step 3: Insert data into the target database
    target_session = TargetSession()

    try:
        target_session.execute(
            text("""
                INSERT INTO past_occupancy_ieq (desk_id, docking_station_id, status, last_updated, temperature, humidity, light, noise)
                VALUES (:desk_id, :docking_station_id, :status, :last_updated, :temperature, :humidity, :light, :noise)
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

# Schedule the task
import schedule

# Run save_live_data every minute (adjust as needed)
schedule.every(1).minute.do(save_live_data)

if __name__ == "__main__":
    print("Scheduler started. Waiting for tasks to run...")
    while True:
        schedule.run_pending()
        time.sleep(1)


'''
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
'''