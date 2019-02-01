'''
Created on 1 Feb 2019

@author: si
'''
import time

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

        self.wait_time_total = 0.
        self.loop_count = 0
        self.loop_last_ran = None

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
