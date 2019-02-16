'''
Created on 1 Feb 2019

@author: si
'''
import os
import time

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pi_fly.model import Sensor, Base


def build_polling_loops(config, scoreboard):
    """
    :param: config dict. like config with `POLLING_LOOPS` as list of dicts.
            probably a flask config object.

    :returns: list of instantiated :class:`pi_fly.polling_loop.PollingLoop`s
            ready from :method:`run_forever` to be run on.
    """
    if isinstance(config, dict):
        loops_config = config['POLLING_LOOPS']
    else:
        loops_config = config.POLLING_LOOPS

    p_loops = []
    for pl_config in loops_config:
        p_loops.append(DevicesPollingLoop(scoreboard, **pl_config))

    return p_loops

class AbstractPollingLoop:
    def __init__(self, scoreboard, **kwargs):
        """
        :param: scoreboard instance of :class:`pi_fly.scoreboard.Scoreboard`.
                Shared memory used to hold data retrieved from sensor. 
        """
        self.scoreboard = scoreboard
        self.name = kwargs.pop('name')
        self.sample_frequency = kwargs.pop('sample_frequency')
        self.description = kwargs.pop('description', None)
        self.log_to_stdout = kwargs.pop('log_to_stdout', False)

        self.wait_time_total = 0.
        self.loop_count = 0
        self.loop_last_ran = None

    def log(self, msg, level="INFO"):
        # TODO wire this to top level's log
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))

    def loop_actions(self):
        """
        What to do each time the loop is run.
        """
        raise NotImplementedError("Should be implemented by sub classes")

    def _single_loop(self):
        """
        :returns: (float) seconds to sleep for before next loop
        """
        self.loop_last_ran = sampling_start_time = time.time()

        # read device is a sensor
        self.loop_actions()

        time_taken = time.time() - sampling_start_time
        wait_for = self.sample_frequency - time_taken
        if wait_for < 0:
            msg = "Couldn't keep up with sampling. Sampling took {} seconds."
            self.log(msg.format(time_taken), "WARNING")
            return 0.

        return wait_for

    def run_forever(self):
        self.log("Running...")
        while True:
            wait_for = self._single_loop()
            self.wait_time_total += wait_for
            self.loop_count += 1
            time.sleep(wait_for)

class DevicesPollingLoop(AbstractPollingLoop):
    def __init__(self, scoreboard, **kwargs):
        """
        Read from input devices and store results on the scoreboard.
        """
        super().__init__(scoreboard, **kwargs)
        self.devices = kwargs.pop('devices')

    def loop_actions(self):
        # read device is a sensor
        for sensor in self.devices:
            r = sensor.get_reading()
            self.scoreboard.update_value(sensor.name, r)
            self.log("Reading: {sensor_id},{value_type},{value_float}".format(**r))

        return True # all OK

class DatabaseStoragePollingLoop(AbstractPollingLoop):
    def __init__(self, scoreboard, db_dsn, **kwargs):
        """
        Read from the scoreboard and store current value for all input devices in DB.
        """
        super().__init__(scoreboard, **kwargs)
        self.sensors_db = db_dsn
        self._db_session = None

    def create_db(self):
        engine = create_engine(self.sensors_db)

        if not os.access(self.sensors_db, os.R_OK):
            self.log("Creating new DB {}".format(self.sensors_db))
        # just update tables
        Base.metadata.create_all(engine)

    @property
    def db_session(self):
        if self._db_session is None:
            engine = create_engine(self.sensors_db)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            self._db_session = DBSession()
        return self._db_session

    def store_reading(self, reading):
        """
        :param: reading (dict) matching keys see :class:`Sensor` model
        """
        r = Sensor(**reading)
        self.db_session.add(r)
        self.db_session.commit()

    def loop_actions(self):

        for device_id, current_value in self.scoreboard.get_all_current_values():
            msg = f"Reading: {device_id}"
            msg += "{sensor_id},{value_type},{value_float}"
            self.log(msg.format(**current_value))
            self.store_reading(current_value)

        return True # all OK
