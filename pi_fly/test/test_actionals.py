'''
Created on 8 May 2019

@author: si
'''
from multiprocessing import Process, Pipe

from pi_fly.actional.abstract import CommsMessage
from pi_fly.actional.actional_management import build_actional_processes, governor_run_forever
from pi_fly.actional.dummy import DummyActional
from pi_fly.devices.dummy import DummyOutput
from pi_fly.scoreboard import ScoreBoard
from pi_fly.test.test_base import BaseTest

class TestActionals(BaseTest):

    def test_communications_channel(self):
        """
        Send a command to the dummy actional and it replies saying the command was accepted.
        It then send a log message as well.
        """
        # this bit will be done in the config file because the actionals available are deployment
        # specific along with the sensors that the actional reads from and the devices it writes
        # to.
        a = DummyActional(name="fake_actional",
                          my_input="the_time",
                          my_output=DummyOutput(name="fake_output")
                          )
        
        # connecting the comms channel isn't done in the config but by a controller that
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
        self.config.ACTIONALS = []
        actional_details = build_actional_processes(self.config, scoreboard)
        self.assertEqual({}, actional_details)

    def test_build_actional_processes(self):
        scoreboard = ScoreBoard()
        actional_details = build_actional_processes(self.config, scoreboard)
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

    def test_governor_run_forever(self):
        """
        Process to read messages from actionals
        """
        scoreboard = ScoreBoard()
        actional_details = build_actional_processes(self.config, scoreboard)
        ac_names = []
        proc_table = []
        for ac_name, ac_parts in actional_details.items():
            # can't pickle a process so just put the comms part on
            scoreboard.update_value(ac_name, {'comms': ac_parts['comms']})
            ac_names.append(ac_name)
            proc_table.append(ac_parts['process'])
            ac_parts['process'].start()

        logging_parent, logging_child = Pipe()
        p = Process(target=governor_run_forever, args=(scoreboard, ac_names, logging_child))
        proc_table.append(p)
        p.start()

        # known name from config of a DummyActional
        pipe_from_scoreboard = scoreboard.get_current_value('fake_actional_0')['comms']
        pipe_from_scoreboard.send(CommsMessage(action="command", message="test_governor_run_forever"))

        msg_count = 0
        while logging_parent.poll(0.5):

            log_msg = logging_parent.recv()
            self.assertIsInstance(log_msg, CommsMessage)
            msg_count += 1

            msg, log_level = log_msg.message
            if 'hello command test_governor_run_forever' in msg or msg_count >= 10:
                self.assertEqual('INFO', log_level)
                break

        self.assertTrue(msg_count < 10, "Couldn't find expected log message")

        for p in proc_table:
            p.terminate()

        for p in proc_table:
            if p.is_alive():
                p.join()

    def test_available_commands(self):

        output = DummyOutput(name="fake_output",
                             set_state_on_start=False
                             )
        a = DummyActional(name="fake_actional",
                          my_input="the_time",
                          my_output=output
                          )
        self.assertEqual(1, len(a.available_commands))
        self.assertEqual('ABC', a.available_commands[0].command)
