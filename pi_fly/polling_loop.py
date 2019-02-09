'''
Created on 1 Feb 2019

@author: si
'''
import time

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
        p_loops.append(PollingLoop(scoreboard, **pl_config))

    return p_loops

class PollingLoop:
    def __init__(self, scoreboard, **kwargs):
        """
        :param: scoreboard instance of :class:`pi_fly.scoreboard.Scoreboard`.
                Shared memory used to hold data retrieved from sensor. 
        """
        self.scoreboard = scoreboard
        self.name = kwargs.pop('name')
        self.sample_frequency = kwargs.pop('sample_frequency')
        self.devices = kwargs.pop('devices')
        self.description = kwargs.pop('description', None)
        self.log_to_stdout = kwargs.pop('log_to_stdout', False)

        self.wait_time_total = 0.
        self.loop_count = 0
        self.loop_last_ran = None

    def log(self, msg, level="INFO"):
        # TODO wire this to top level's log
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))

    def _single_loop(self):
        """
        :returns: (float) seconds to sleep for before next loop
        """
        self.loop_last_ran = sampling_start_time = time.time()

        # read device is a sensor
        for sensor in self.devices:
            r = sensor.get_reading()
            self.scoreboard.update_value(sensor.name, r)
            self.log("Reading: {sensor_id},{value_type},{value_float}".format(**r))

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
