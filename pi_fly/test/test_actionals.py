'''
Created on 8 May 2019

@author: si
'''
from multiprocessing import Process, Pipe

from pi_fly.actional.abstract import CommsMessage
from pi_fly.actional.dummy import DummyActional
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
                      log_messages,
                      "DummyActional.run_command didn't run")

        self.assertIn('dummy action is running',
                      log_messages,
                      "DummyActional.actional_loop_actions fail")
