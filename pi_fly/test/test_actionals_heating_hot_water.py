"""
Created on 19 Feb 2026

@author: si
"""
from multiprocessing import Pipe

from pi_fly.actional.abstract import CommsMessage
from pi_fly.actional.heating_hot_water import HeatingHotWater
from pi_fly.devices.dummy import DummyOutput
from pi_fly.scoreboard import ScoreBoard
from pi_fly.test.test_base import BaseTest


class TestActionalsHeatingHotWater(BaseTest):
    def test_manual_hotwater(self):
        """
        Command to run hot water switches relay on.
        """
        hotwater_relay = DummyOutput(
            name="fake_relay_hotwater",
            set_state_on_start=False,
            min_switching_time=0.00001,
        )

        heating_relay = DummyOutput(
            name="fake_relay_heating",
            set_state_on_start=False,
            min_switching_time=0.00001,
        )

        boiler = HeatingHotWater(
            name="boiler",
            db_dsn="",
            hot_water_top="",
            house_inside_landing="",
            central_heating=heating_relay,
            hot_water=hotwater_relay,
            log_to_stdout=False,
        )

        scoreboard = ScoreBoard()
        boiler.set_scoreboard(scoreboard)

        # connecting the comms channel isn't done in the profile but by a controller that
        # also instantiates the actional into it's own Process.
        parent_conn, child_conn = Pipe()
        boiler.set_comms_channel(child_conn)

        boiler.loop_actions()
        self.assertFalse(hotwater_relay.state, "Should be False before command")

        # send manual command
        parent_conn.send(CommsMessage(action="command", message="hotwater:20"))
        boiler.loop_actions()
        self.assertTrue(hotwater_relay.state, "Relay should be on")
