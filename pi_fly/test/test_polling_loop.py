'''
Created on 1 Feb 2019

@author: si
'''
import sqlite3

from pi_fly.devices.dummy import DummyInput
from pi_fly.polling_loop import DevicesPollingLoop, build_device_polling_loops,\
                                DatabaseStoragePollingLoop
from pi_fly.scoreboard import ScoreBoard
from pi_fly.settings.test_config import Config

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
        polling_loops = build_device_polling_loops(self.config, scoreboard)

        self.assertEqual(1, len(polling_loops))
        p_test_loop = polling_loops[0]

        # check it's a valid polling loop by running it
        wait_time = p_test_loop._single_loop()
        self.assertTrue(wait_time >= 0)

        # DummyInput should write unix epoc time to the scoreboard
        # time must be greater than when I wrote this test
        time_sensor_data = scoreboard.get_current_value("fake_input")
        self.assertTrue(time_sensor_data['value_float'] > 1549747311)

    def test_database_storage_polling_loop(self):
        """
        db storage reads from scoreboard and writes to DB.
        """
        scoreboard = ScoreBoard()
        devices = [DummyInput(name="fake_0"),
                   DummyInput(name="fake_1"),
                   ]

        # make devices store something on scoreboard
        devices_loop = DevicesPollingLoop(scoreboard,
                                    name="a_loop",
                                    sample_frequency=0.1,
                                    devices=devices
                                    )
        devices_loop._single_loop()

        # can DB loop see these values

        # Memory doesn't seem to create tables?  e.g. 'sqlite:///:memory:' so
        # using temp file.
        config = Config()
        db_loop = DatabaseStoragePollingLoop(scoreboard,
                                             config.SQLALCHEMY_DATABASE_URI,
                                             name="db_loop",
                                             sample_frequency=600,
                                            )
        db_loop.create_db()
        db_loop._single_loop()


        # Read from DB (without sqlalchemy) and get values for both fake sensors
        db_connection=sqlite3.connect(config.DB_FILE)
        db_cursor=db_connection.cursor()
        db_cursor.execute("select value_float from sensor")
        rows = [r for r in db_cursor.fetchall()]

        self.assertEqual(2, len(rows), "Two sensors")
        for r in rows:
            self.assertTrue(r[0] > 1550437321, "Time recorded is ahead of time test written.")

        # clean up temp file
        config.drop_db()
