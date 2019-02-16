'''
Created on 1 Feb 2019

@author: si
'''
from pi_fly.devices.dummy import DummyInput
from pi_fly.polling_loop import DevicesPollingLoop, build_polling_loops
from pi_fly.scoreboard import ScoreBoard

from .test_base import BaseTest

class TestPollingLoop(BaseTest):

    def test_device_read(self):
        """
        Poll a single (dummy) device once. Check a wiat time (for next loop)
        is returned and check a value is read.
        """

        scoreboard = ScoreBoard()
        devices = [DummyInput(name="fake_input")]
        
        p_loop = DevicesPollingLoop(scoreboard,
                                    name="a_loop",
                                    sample_frequency=0.1,
                                    devices=devices
                                    )
        wait_time = p_loop._single_loop()
        self.assertTrue(wait_time >= 0)

        # DummyInput should write unix epoc time to the scoreboard
        # time must be greater than when I wrote this test
        time_sensor_data = scoreboard.get_current_value("fake_input")
        self.assertTrue(time_sensor_data['value_float'] > 1549043210)

    def test_loops_from_config(self):
        """
        Build PollingLoops from config variables.
        """
        scoreboard = ScoreBoard()
        polling_loops = build_polling_loops(self.config, scoreboard)

        self.assertEqual(1, len(polling_loops))
        p_test_loop = polling_loops[0]

        # check it's a valid polling loop by running it
        wait_time = p_test_loop._single_loop()
        self.assertTrue(wait_time >= 0)

        # DummyInput should write unix epoc time to the scoreboard
        # time must be greater than when I wrote this test
        time_sensor_data = scoreboard.get_current_value("fake_input")
        self.assertTrue(time_sensor_data['value_float'] > 1549747311)

