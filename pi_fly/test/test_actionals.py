'''
Created on 8 May 2019

@author: si
'''
from datetime import datetime
from multiprocessing import Process, Pipe

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pi_fly.actional.abstract import CommsMessage
from pi_fly.actional.actional_management import build_actional_processes, governor_run_forever
from pi_fly.actional.dummy import DummyActional
from pi_fly.actional.solar_thermal import SolarThermal
from pi_fly.devices.dummy import DummyOutput
from pi_fly.model import Base, Event
from pi_fly.scoreboard import ScoreBoard
from pi_fly.test.test_base import BaseTest


class TestActionals(BaseTest):

    def test_communications_channel(self):
        """
        Send a command to the dummy actional and it replies saying the command was accepted.
        It then send a log message as well.
        """
        # this bit will be done in the profile file because the actionals available are deployment
        # specific along with the sensors that the actional reads from and the devices it writes
        # to.
        a = DummyActional(name="fake_actional",
                          my_input="the_time",
                          my_output=DummyOutput(name="fake_output")
                          )

        # connecting the comms channel isn't done in the profile but by a controller that
        # also instantiates the actional into it's own Process.
        parent_conn, child_conn = Pipe()
        a.set_comms_channel(child_conn)

        p = Process(target=a)
        p.start()

        parent_conn.send(CommsMessage(action="command", message="hello"))
        parent_conn.send(CommsMessage(action="command", message="terminate"))

        comms_messages_recieved = []
        while True:
            if parent_conn.poll(0.1):
                comms_messages_recieved.append(parent_conn.recv())

            if not p.is_alive():
                break

        p.join()
        log_messages = [cm.message for cm in comms_messages_recieved]
        self.assertIn('hello command hello',
                      str(log_messages),
                      "DummyActional.run_command didn't run")

        self.assertIn('dummy actional (fake_actional) is running',
                      str(log_messages),
                      "DummyActional.actional_loop_actions fail")

    def test_scoreboard_io(self):
        """
        Input and output to the scoreboard
        """
        a = DummyActional(name="fake_actional",
                          my_input="the_time",
                          my_output=DummyOutput(name="fake_output")
                          )
        scoreboard = ScoreBoard()
        a.set_scoreboard(scoreboard)

        # put something onto the scoreboard for the dummy actional to read
        fake_sensor_output = {'sensor_id': None,
                              'value_type': "time",
                              'value_float': 42
                              }
        scoreboard.update_value('the_time', fake_sensor_output)

        # :method:`actional_loop_actions` is normally called once per loop.
        # The dummy actional looks for the scoreboard value for it's 'my_input' and responds by
        # doubling the number it finds and putting this value back on the scoreboard under device
        # name 'actional_reply'
        a.actional_loop_actions()

        reply = scoreboard.get_current_value('actional_reply')
        self.assertEqual(84, reply)

    def test_output_device(self):
        """
        On receiving the pre-agree magic number 123 from the input device, set the output device
        to True.
        """
        output = DummyOutput(name="fake_output",
                             set_state_on_start=False
                             )
        a = DummyActional(name="fake_actional",
                          my_input="the_time",
                          my_output=output
                          )
        scoreboard = ScoreBoard()
        a.set_scoreboard(scoreboard)
        fake_sensor_output = {'sensor_id': None,
                              'value_type': "time",
                              'value_float': 123
                              }
        scoreboard.update_value('the_time', fake_sensor_output)

        self.assertFalse(output.state)
        a.actional_loop_actions()
        self.assertTrue(output.state)

    def test_build_actional_processes_nothing(self):
        scoreboard = ScoreBoard()
        self.profile.ACTIONALS = []
        actional_details = build_actional_processes(self.profile, scoreboard)
        self.assertEqual({}, actional_details)

    def test_build_actional_processes(self):
        scoreboard = ScoreBoard()
        actional_details = build_actional_processes(self.profile, scoreboard)
        self.assertEqual(2, len(actional_details))

    def test_pipe_on_the_scoreboard(self):
        """
        The scoreboard is a grouping of shared variables and uses :class:`multiprocessing.Manager`
        to keep access thread/process safe. Can pipes be shared?!
        """
        scoreboard = ScoreBoard()
        parent_conn, child_conn = Pipe()
        scoreboard.update_value('message_pipe', parent_conn)

        child_conn.send("hello pipe!")

        pipe_from_scoreboard = scoreboard.get_current_value('message_pipe')
        received_value = pipe_from_scoreboard.recv()
        self.assertEqual("hello pipe!", received_value)

    def build_governor(self, scoreboard, expected_log_message, messages_to_send):
        """
        Args:
            expected_log_message (str) - finish immediately when this message is received.
            messages_to_send (list of CommsMessage) to send to fake_actional_0
        """
        actional_details = build_actional_processes(self.profile, scoreboard)
        ac_names = []
        proc_table = []
        for ac_name, ac_parts in actional_details.items():
            # can't pickle a process so just put the comms part on
            scoreboard.update_value(ac_name, {'comms': ac_parts['comms']})
            ac_names.append(ac_name)
            proc_table.append(ac_parts['process'])
            ac_parts['process'].start()

        logging_parent, logging_child = Pipe()
        governor_kwargs = {'scoreboard': scoreboard,
                           'actional_names': ac_names,
                           'profile': self.profile,
                           'logging_pipe': logging_child
                           }
        p = Process(target=governor_run_forever, kwargs=governor_kwargs)
        proc_table.append(p)
        p.start()

        # known name from profile of a DummyActional
        pipe_from_scoreboard = scoreboard.get_current_value('fake_actional_0')['comms']
        for comms_message in messages_to_send:
            pipe_from_scoreboard.send(comms_message)

        msgs = []
        max_messages = 20  # more than this means fail
        while logging_parent.poll(1):

            log_msg = logging_parent.recv()
            self.assertIsInstance(log_msg, CommsMessage)

            msg = log_msg.message[0]
            msgs.append(msg)
            if expected_log_message in msg:
                break

            if len(msgs) >= max_messages:
                break

        for p in proc_table:
            p.terminate()

        for p in proc_table:
            if p.is_alive():
                p.join()

        return msgs

    def test_governor_run_forever(self):
        """
        Read log messages from actionals that are being run by the governor.
        """
        scoreboard = ScoreBoard()
        expected_log_message = 'hello command hello'
        test_command = [CommsMessage(action="command", message="hello"), ]
        log_msgs = self.build_governor(scoreboard,
                                       expected_log_message=expected_log_message,
                                       messages_to_send=test_command
                                       )
        self.assertIn(expected_log_message, "".join(log_msgs), "Couldn't find expected log message")

    def test_available_commands(self):

        output = DummyOutput(name="fake_output",
                             set_state_on_start=False
                             )
        a = DummyActional(name="fake_actional",
                          my_input="the_time",
                          my_output=output
                          )
        self.assertEqual(2, len(a.available_commands))
        dummy_actional_commands = set([ax.command for ax in a.available_commands])
        self.assertEqual(set(['hello', 'send_event']), dummy_actional_commands)

    def test_solar_thermal(self):

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

    def test_solar_thermal_pump_event(self):
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

    def test_event(self):
        """
        Test the dummy actional can send an event that would get back to the governor and then on to database.
        """
        # database is normally created by the DatabaseStoragePollingLoop and web view
        # consumes from this db. But this unit test shouldn't be concerned with
        # DatabaseStoragePollingLoop so doing own create.
        engine = create_engine(self.profile.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        db_session = DBSession()

        all_events = [r for r in db_session.query(Event).all()]
        self.assertEqual(0, len(all_events), "DB table should be empty")

        scoreboard = ScoreBoard()
        expected_log_message = 'example event sent'
        test_command = [CommsMessage(action="command", message="send_event"),
                        CommsMessage(action="command", message="terminate"),
                        ]
        log_msgs = self.build_governor(scoreboard,
                                       expected_log_message=expected_log_message,
                                       messages_to_send=test_command
                                       )
        self.assertIn(expected_log_message, "".join(log_msgs), "Couldn't find expected log message")

        all_events = [r for r in db_session.query(Event).all()]
        self.assertEqual(1, len(all_events), "One event should be in the DB")

        test_event = all_events[0]
        self.assertIsInstance(test_event.start, datetime)
        self.assertIsInstance(test_event.end, datetime)
        self.assertEqual(test_event.source, 'fake_actional_0')
        self.assertEqual(test_event.label, 'example event')
