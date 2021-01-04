'''
Created on 15 Apr 2018

@author: si
'''
from datetime import datetime

from flask import Flask, render_template, current_app, abort, request
from flask_sqlalchemy import SQLAlchemy

from pi_fly.actional.abstract import CommsMessage
from pi_fly.devices.abstract import AbstractSensor
from pi_fly.model import Sensor

db = SQLAlchemy()


def create_app(profiles_class, scoreboard):
    """
    :param profiles_class (str or class) to Flask settings
    :param scoreboard instance of :class:`pi_fly.scoreboard.ScoreBoard`
    """
    app = Flask(__name__)
    app.config.from_object(profiles_class)
    db.init_app(app)

    app.sensor_scoreboard = scoreboard

    @app.route('/')
    def dashboard():
        hot_water_sensor_id = "28-0015231007ee"
        last_reading = db.session.query(Sensor)\
            .order_by(Sensor.last_updated.desc())\
            .filter(Sensor.sensor_id == hot_water_sensor_id)\
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
        sensor_values = {k: v for k, v in current_app.sensor_scoreboard.get_all_current_values()}
        p = {}  # sensor name => {'display_value': '', 'display_class': ''}
        for input_device in current_app.config['INPUT_DEVICES']:
            assert isinstance(input_device, AbstractSensor)
            if input_device.name in sensor_values:
                v = sensor_values[input_device.name]
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

        page_vars = dict(sensors=p)
        return render_template("sensor_scoreboard.html", **page_vars)

    @app.route('/run_command/', methods=['GET', 'POST'])
    def run_actional_command():
        """
        GET lists available commands
        POST Sends a user selected command to an actional
        """
        ac_command = {}
        for ac in current_app.config['ACTIONALS']:
            ac_command[ac.name] = []
            for command_template in ac.available_commands:
                cmd_summary = (command_template.command, command_template.description)
                ac_command[ac.name].append(cmd_summary)
        page_vars = {'actionals_with_commands': ac_command}

        if request.method == 'POST':
            target_actional = request.values.get('actional_name', None)
            target_command = request.values.get('command', None)
            if target_actional not in ac_command:
                abort(400, "Unknown actional {}".format(target_actional))

            try:
                actional_comms = scoreboard.get_current_value(target_actional)['comms']
            except KeyError:
                abort(500, "Actional not found in the scoreboard")

            actional_comms.send(CommsMessage(action="command", message=target_command))
            msg = "Running....{} .. {}".format(target_actional, target_command)
            page_vars['message'] = msg

        return render_template("run_command.html", **page_vars)

    return app
