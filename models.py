from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    # CREATE TABLE user (id SERIAL PRIMARY KEY, email VARCHAR(100) UNIQUE NOT NULL, ...)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    role = db.Column(db.String(10), default='user')  # 'user'||'admin'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Sensor(db.Model):
    # CREATE TABLE sensor (id SERIAL PRIMARY KEY, name VARCHAR(100), lat FLOAT, lon FLOAT, description VARCHAR(255))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)        # city name e.g. 'Arta'
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    measurements = db.relationship('Measurement', backref='sensor', lazy=True)
    # relationship: one sensor -> many measurements

class MeasurementCategory(db.Model):
    # CREATE TABLE measurement_category (id SERIAL PRIMARY KEY, name VARCHAR(50))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)         # 'temperature' or 'humidity'
    measurements = db.relationship('Measurement', backref='category', lazy=True)

class Measurement(db.Model):
    # CREATE TABLE measurement (id SERIAL PRIMARY KEY, sensor_id INT REFERENCES sensor(id),
    # category_id INT REFERENCES measurement_category(id), value FLOAT, timestamp TIMESTAMP)
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('measurement_category.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)             # temp or humidity value
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)