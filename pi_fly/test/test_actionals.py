'''
Created on 8 May 2019

@author: si
'''
from multiprocessing import Process, Pipe

from pi_fly.actional.dummy import DummyActional

from .test_base import BaseTest

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




        parent_conn.send("hello")

        print(parent_conn.recv())
        p.join()