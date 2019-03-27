'''
Created on 15 Apr 2018

@author: si
'''
from datetime import datetime

from flask import Flask, Response, render_template, current_app
from flask_sqlalchemy import SQLAlchemy

from pi_fly.devices.abstract import AbstractSensor
from pi_fly.model import Sensor

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
        if last_reading is None:
            return render_template("user_message.html", **{'msg': 'No sensor readings in DB.'})

        d = datetime.utcnow() - last_reading.last_updated
        minutes_since_reading = d.total_seconds() / 60.
        page_vars = {'collection_failure': minutes_since_reading > 10.,
                     'water_temp': last_reading.value_float,
                     'bath_possible': last_reading.value_float > 45.,
                     'last_read_at': last_reading.last_updated,
                    }

        return render_template("dashboard.html", **page_vars)

    @app.route('/sensor_scoreboard/')
    def sensor_scoreboard():
        """
        Show the current values for all input devices in the config.
        """
        # consolidate all sensors on the scoreboard with all input devices listed in
        # the config. Give a warning message when these don't tally.
        sensor_values = {k: v for k,v in current_app.sensor_scoreboard.get_all_current_values()}
        p = {} # sensor name => {'display_value': '', 'display_class': ''}
        for input_device in current_app.config['INPUT_DEVICES']:
            assert isinstance(input_device, AbstractSensor)
            if input_device.name in sensor_values:
                v = sensor_values[input_device.name]
                if v['value_type'] == "temperature":
                    dv = v['value_float']
                else:
                    dv = v['value_type'] + ':' + str(v['value_float'])

            display = {'display_value': dv,
                       'display_class': '',
                       }
            p[input_device.name] = display

        for name, values in sensor_values.items():
            if name not in p:
                # in scoreboard but not in config??
                p[name] = {'display_value': str(values),
                           'display_class': 'WARNING',
                           }

        page_vars = dict(sensors = p)
        return render_template("sensor_scoreboard.html", **page_vars)

    return app

if __name__ == '__main__':
    app = create_app('settings.local_config.Config')
    app.run(debug=app.config['DEBUG'], use_reloader=False, port=6010)
