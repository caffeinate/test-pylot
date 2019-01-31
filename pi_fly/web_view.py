'''
Created on 15 Apr 2018

@author: si
'''
from datetime import datetime

from flask import Flask, Response, render_template, current_app
from flask_sqlalchemy import SQLAlchemy

from model import Sensor

db = SQLAlchemy()

def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)
    db.init_app(app)

    @app.route('/')
    def dashboard():
        hot_water_sensor_id = "28-0015231007ee"
        last_reading = db.session.query(Sensor)\
                            .order_by(Sensor.last_updated.desc())\
                            .filter(Sensor.sensor_id==hot_water_sensor_id)\
                            .first()

        d = datetime.utcnow() - last_reading.last_updated
        minutes_since_reading = d.total_seconds() / 60.
        page_vars = {'collection_failure': minutes_since_reading > 10.,
#                      'water_temp': last_reading.value_float,
                     'water_temp': current_app.shared_data['counter'],
                     'bath_possible': last_reading.value_float > 45.,
                     'last_read_at': last_reading.last_updated,
                    }

        return render_template("dashboard.html", **page_vars)

    return app


if __name__ == '__main__':
    app = create_app('settings.local_config.Config')
    app.run(debug=app.config['DEBUG'], use_reloader=False, port=6010)
