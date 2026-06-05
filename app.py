
from asyncio import run
from models import User, Sensor, Measurement, MeasurementCategory
from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
from email_validator import validate_email, EmailNotValidError
from extensions import db, login_manager, mail #a file made to hold all current and future ext's
from admin_routes import init_admin_routes
import random
from flask_mail import Message
from pprint import pprint
import requests
from flask_admin import Admin
from sqlalchemy import desc
import os
import schedule
import time
import threading
app = Flask(__name__)
admin=Admin()
app.config.from_pyfile("config.py")# Load configuration from config.py prettier than not
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

from models import User
@login_manager.user_loader   #Flask-Login needs this function to load the user from the userId..
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False
@app.route('/')
def index():
  return redirect(url_for('signup'))#@login_required fix me first please 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not validate_email_address(email):
            flash('Invalid email address.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found. Please sign up first.', 'error')
            return redirect(url_for('signup'))
        
        if not user.check_password(password):
            flash('Wrong password.', 'error')
            return render_template('login.html')
        
        if not user.is_verified:
            flash('Please verify your email first.', 'error')
            return render_template('login.html')
        
        from flask_login import login_user
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if len(password) < 6 or len(password) > 50: #password length check
            flash('Password must be between 6 and 50 characters long.', 'error')
            return render_template('signup.html')
        elif not any(char.isdigit() for char in password): #password must contain at least one number 
            flash('Password must contain at least one number.', 'error')
            return render_template('signup.html')
        elif not any(char.isalpha() for char in password): #password must contain at least one letter
            flash('Password must contain at least one letter.', 'error')
            return render_template('signup.html')
        if not validate_email_address(email):
            flash('Invalid email address.', 'error')
            return render_template('signup.html')
        if User.query.filter_by(email=email).first():#SELECT * FROM user WHERE email = 'whatever@gmail.com' LIMIT 1
            flash('Email already registered. Try logging in.', 'error')
            return render_template('signup.html')
        session['pending_email'] = email              
        new_user = User(email=email)
        new_user.set_password(password) 
        db.session.add(new_user)    
        db.session.commit()
        send_verification_code(new_user, email)
        return redirect(url_for('verify'))
    else:
        return render_template('signup.html')
def send_verification_code(user, email):
    code = random.randint(100000, 999999)
    user.verification_code = str(code)
    db.session.commit()
    msg = Message(
        subject='Your verification code',
        recipients=[email],
        body=f'This was compeletely free btw isnt this awesome :Code is : {code}'
    )
    mail.send(msg)
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if not session.get('pending_email'):
      return redirect(url_for('signup'))          ####!!MAK ETHE DB SAVE THE USER 
    if request.method == 'POST':                     ######ONLY AFTER VERIFICATION AND NOT BEFORE
        code = request.form.get('code', '').strip()   # Use .get() instead of request.form['code'] to avoid KeyError if 'code' is missing
        email = session.get('pending_email') # gt crasharei alliws idk 
        user = User.query.filter_by(email=email).first()
     #   if user.verification_code == code: an to afisw etsi den doulevei de jerw giati 
        if str(user.verification_code) == str(code):
            user.is_verified = True
            user.verification_code = None  # diwxto meta aptin if giati alliws to zitaei sunexeia paei se inf loop
            session.pop('pending_email', None)  # Clear session
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('Wrong code.', 'error')
    return render_template('verify.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    cities_data = cards()  # tovala se function gia scalability#
    recent_measurements = Measurement.query.order_by(desc(Measurement.timestamp)).limit(20).all()
    if request.method == 'POST':
        input_city = request.form['city']
        data = collect_data(input_city)
        if data.get('cod') != 200:
            flash('City not found. Please enter a valid city name.', 'error')
        return render_template(
            'dashboard.html',
            cities_data=cities_data,
            data=data,
            measurements=recent_measurements,
        )
    return render_template('dashboard.html', cities_data=cities_data, measurements=recent_measurements)
def cards():
    city_data={
    'Arta': collect_data('Arta'),
    'Nafplio': collect_data('Nafplio'),
    'Kozani': collect_data('Kozani'),
    'Ioannina': collect_data('Ioannina'),
    }
    return city_data

def collect_data(city):
     
        res=requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={app.config['W_KEY']}&units=metric").json()
        temp = res["main"]["temp"]
        feels_like = res["main"]["feels_like"]
        humidity = res["main"]["humidity"]
        description = res["weather"][0]["description"]
        wind_speed = res["wind"]["speed"]
        clouds = res["clouds"]["all"]
        country = res["sys"]["country"]
      #  print(f"{city}, {country} | {temp}°C (feels {feels_like}°C) | {description} | Humidity: {humidity}% | Wind: {wind_speed}m/s | Clouds: {clouds}%")
        return res#131-139 tha fugei to xw ia testnig purposes 

def fetch_and_store_all_cities():
    with app.app_context():
        cities = ['Arta', 'Nafplio', 'Kozani', 'Ioannina']
        for city in cities:
            res = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={app.config['W_KEY']}&units=metric"
            ).json()
            if res.get('cod') == 200:
                sensor = Sensor.query.filter_by(name=city).first()
                if not sensor:
                    coord = res.get('coord', {})
                    sensor = Sensor(
                        name=city,
                        lat=coord.get('lat', 0.0),
                        lon=coord.get('lon', 0.0),
                        description=res.get('weather', [{}])[0].get('description', ''),
                    )
                    db.session.add(sensor)
                    db.session.commit()
                temp_cat = MeasurementCategory.query.filter_by(name='temperature').first()
                if not temp_cat:
                    temp_cat = MeasurementCategory(name='temperature')
                    db.session.add(temp_cat)
                    db.session.commit()
                hum_cat = MeasurementCategory.query.filter_by(name='humidity').first()
                if not hum_cat:
                    hum_cat = MeasurementCategory(name='humidity')
                    db.session.add(hum_cat)
                    db.session.commit()
                db.session.add(
                    Measurement(
                        sensor_id=sensor.id,
                        category_id=temp_cat.id,
                        value=res['main']['temp'],
                    )
                )
                db.session.add(
                    Measurement(
                        sensor_id=sensor.id,
                        category_id=hum_cat.id,
                        value=res['main']['humidity'],
                    )
                )
        db.session.commit()


def start_hourly_scheduler():
    schedule.every().minute.do(fetch_and_store_all_cities) #tha ginei .hour in production, .minute for testing

    def run():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run, daemon=True)#threads gia na trexei PARALILA ME TO IPOLIPO
    thread.start()


def get_city_temp_hum_series(city, interval='hourly', max_points=100):
    """Return ordered timestamp, temperature, and humidity series for the city."""
    sensor = Sensor.query.filter_by(name=city).first()
    if not sensor:
        return [], [], []

    temp_cat = MeasurementCategory.query.filter_by(name='temperature').first()
    hum_cat = MeasurementCategory.query.filter_by(name='humidity').first()
    if not temp_cat or not hum_cat:
        return [], [], []

    # pairnoume ta teleutaia 500 records gia ka8e kathgoria
    temp_measurements = (
        Measurement.query
        .filter_by(sensor_id=sensor.id, category_id=temp_cat.id)
        .order_by(Measurement.timestamp.desc())
        .limit(500)
        .all()
    )
    hum_measurements = (
        Measurement.query
        .filter_by(sensor_id=sensor.id, category_id=hum_cat.id)
        .order_by(Measurement.timestamp.desc())
        .limit(500)
        .all()
    )

    # Reverse to chronological order.
    temp_measurements = list(reversed(temp_measurements))
    hum_measurements = list(reversed(hum_measurements))

    if interval == 'minute':
        # ston minute mode pairnoume aplo raw teleutaia data stoixeia
        series_temp = temp_measurements[-max_points:]
        series_hum = hum_measurements[-max_points:]
        timestamps = [m.timestamp.strftime('%Y-%m-%d %H:%M:%S') for m in series_temp]
        temps = [m.value for m in series_temp]
        hums = [m.value for m in series_hum]
        return timestamps, temps, hums

    # gia hourly/daily xreiazomaste aggregation, den einai raw minutes
    def aggregate(measurements, bucket):
        points = []
        current_key = None
        current_values = []

        for m in measurements:
            key = bucket(m.timestamp)
            if key != current_key and current_key is not None:
                points.append((current_key, sum(current_values) / len(current_values)))
                current_values = []
            current_key = key
            current_values.append(m.value)

        if current_key is not None and current_values:
            points.append((current_key, sum(current_values) / len(current_values)))

        return points[-max_points:]

    if interval == 'daily':
        # daily = kathe mera, xrisimopoiei tin imerominia mono
        bucket = lambda ts: ts.strftime('%Y-%m-%d')
    else:
        # hourly = group by ora, kathe ora exei ena average
        bucket = lambda ts: ts.strftime('%Y-%m-%d %H:00:00')

    temp_points = aggregate(temp_measurements, bucket)
    hum_points = aggregate(hum_measurements, bucket)

    timestamps = [p[0] for p in temp_points]
    temps = [p[1] for p in temp_points]
    hums = [p[1] for p in hum_points]
    return timestamps, temps, hums


# Initialize admin routes
init_admin_routes(app)

@app.route('/graph-data/<city>')
def graph_data(city):
    # to frontend mporei na zitisei interval=minute/hourly/daily
    interval = request.args.get('interval', 'hourly')
    timestamps, temps, hums = get_city_temp_hum_series(city, interval=interval)
    return jsonify({
        'city': city,
        'interval': interval,
        'timestamps': timestamps,
        'temperature': temps,
        'humidity': hums,
    })

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        start_hourly_scheduler()
    app.run(debug=True, host='0.0.0.0', port=5000)  

