'''
Run web view with gunicorn

Created on 22 Apr 2018

@author: si
'''
from multiprocessing import Process
import sys

import gunicorn.app.base

from pi_fly.actional.actional_management import build_actional_processes, governor_run_forever
from pi_fly.polling_loop import DatabaseStoragePollingLoop, build_device_polling_loops
from pi_fly.scoreboard import ScoreBoard
from pi_fly.web_view import create_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run_forever(profile_label):

    scoreboard = ScoreBoard()  # for storing sensor values
    app = create_app('profiles.%s_config.Config' % profile_label, scoreboard)

    # read input device loops from config and make a Proc per loop
    # proc instead of async because of isolation in event of lock or exception or other failure
    process_list = []
    polling_loops = build_device_polling_loops(app.config, scoreboard)
    for device_polling_loop in polling_loops:
        p = Process(target=device_polling_loop)
        p.start()
        process_list.append(p)

    # proc to store values into DB
    db_loop = DatabaseStoragePollingLoop(scoreboard,
                                         app.config['SQLALCHEMY_DATABASE_URI'],
                                         name="db_loop",
                                         sample_frequency=5 * 60,
                                         log_to_stdout=True,
                                         )
    db_loop.create_db()
    p = Process(target=db_loop)
    p.start()
    process_list.append(p)

    # Actionals take an action based on inputs.
    actional_details = build_actional_processes(app.config, scoreboard)
    actional_names = []
    for actional_name, actional_details in actional_details.items():
        actional_names.append(actional_name)
        actional_details['process'].start()
        process_list.append(actional_details['process'])
        # communications channel (instance of :class:`multiprocessing.Pipe`) is kept on the
        # scoreboard so other processes can communicate with the actionals
        scoreboard.update_value(actional_name, {'comms': actional_details['comms']})

    governor_proc = Process(target=governor_run_forever, args=(scoreboard, actional_names,))
    governor_proc.start()
    process_list.append(governor_proc)

    options = {
        'bind': '%s:%s' % ('0.0.0.0', app.config.get('HTTP_PORT', '80')),
        'workers': 2,
    }

    StandaloneApplication(app, options).run()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        msg = "usage: python main.py <profile label>\n"
        sys.stderr.write(msg)
        sys.exit(-1)

    run_forever(sys.argv[1])
