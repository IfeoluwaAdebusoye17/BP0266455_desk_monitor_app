from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
database_uri = os.getenv('SQL_DATABASE_URI')

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# Initialize Flask app and Celery
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgrestill100k$@localhost/office_management'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # Redis as the broker
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # Redis as the result backend

db = SQLAlchemy(app)
celery = make_celery(app)
