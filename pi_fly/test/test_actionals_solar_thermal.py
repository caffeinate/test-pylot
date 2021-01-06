'''
Created on 6 Jan 2021

@author: si
'''
from multiprocessing import Pipe

from pi_fly.actional.solar_thermal import SolarThermal
from pi_fly.devices.dummy import DummyOutput
from pi_fly.scoreboard import ScoreBoard
from pi_fly.test.test_base import BaseTest


class TestActionalsSolarThermal(BaseTest):

    def test_pump_on_temperature_difference(self):

        solar_pump = DummyOutput(name="fake_solar_pump",
                                 set_state_on_start=False,
                                 min_switching_time=0.00001,  # set on start is just before actional's action
                                 )

        solar = SolarThermal(name="solar_thermal",
                             hot_water_bottom="hot_water_fake",
                             solar_collector="solar_collector_fake",
                             solar_pump=solar_pump,
                             log_to_stdout=False,
                             )

        scoreboard = ScoreBoard()
        solar.set_scoreboard(scoreboard)

        fake_sensor_output = {'sensor_id': None,
                              'value_type': "temperature",
                              'value_float': 42.3
                              }
        scoreboard.update_value('solar_collector_fake', fake_sensor_output)

        fake_sensor_output = {'sensor_id': None,
                              'value_type': "temperature",
                              'value_float': 24.0
                              }
        scoreboard.update_value('hot_water_fake', fake_sensor_output)

        self.assertFalse(solar_pump.state)
        solar.actional_loop_actions()
        self.assertTrue(solar_pump.state)

    def test_pump_event(self):
        """
        Check that pump on and then pump off should be logged as one event. This in the real
        system would be stored in the DB by the governor. This test checks the `event` message
        is put onto the multiprocessing pipe that connects back to the governor.
        """
        solar_pump = DummyOutput(name="fake_solar_pump",
                                 set_state_on_start=False,
                                 min_switching_time=0.00001,  # set on start is just before actional's action
                                 )

        solar = SolarThermal(name="solar_thermal",
                             hot_water_bottom="hot_water_fake",
                             solar_collector="solar_collector_fake",
                             solar_pump=solar_pump,
                             log_to_stdout=False,
                             )

        scoreboard = ScoreBoard()
        solar.set_scoreboard(scoreboard)

        # connecting the comms channel isn't done in the profile but by a controller that
        # also instantiates the actional into it's own Process.
        parent_conn, child_conn = Pipe()
        solar.set_comms_channel(child_conn)

        self.assertEqual(False,
                         solar_pump.state,
                         "Pump state should be false, not None at start of test."
                         )

        def send_fake_solar_sensor_values(collector_value, hot_water_value):

            for sensor_name, sensor_value in [('solar_collector_fake', collector_value),
                                              ('hot_water_fake', hot_water_value)
                                              ]:
                sensor_value = {'sensor_id': None,
                                'value_type': "temperature",
                                'value_float': sensor_value
                                }
                scoreboard.update_value(sensor_name, sensor_value)

        send_fake_solar_sensor_values(35.0, 10.2)
        solar.actional_loop_actions()
        send_fake_solar_sensor_values(35.0, 34.9)
        solar.actional_loop_actions()

        comms_messages_recieved = []
        while parent_conn.poll(0.1):
            comms_messages_recieved.append(parent_conn.recv())

        events = [cm for cm in comms_messages_recieved if cm.action == 'event']

        self.assertEqual(1, len(events), "only expecting 1 pump running event")
        self.assertEqual('pump running', events[0].message)
        self.assertTrue(events[0].date_stamp < events[0].date_stamp_end)
