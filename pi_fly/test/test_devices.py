'''
Created on 22 Apr 2019

@author: si
'''
import time

from pi_fly.devices.abstract import AbstractOutput
from pi_fly.devices.dummy import DummyOutput

from .test_base import BaseTest

class TestDevices(BaseTest):

    def test_output_set_state_on_start(self):
        # state on start not specified
        output = DummyOutput(name="fake_input")
        self.assertEqual(None, output.state)
                
        output = DummyOutput(name="fake_output",
                             set_state_on_start=True
                             )
        self.assertTrue(output.state)

    def test_output_time_limited_state_changes(self):
        # safe switching > 10 ms
        output = DummyOutput(name="fake_input")
        self.assertEqual(AbstractOutput.SetState.OK, output.set_state(True))
        time.sleep(0.011)
        self.assertEqual(AbstractOutput.SetState.OK, output.set_state(False))
        self.assertFalse(output.state)

        # fast switching, switch not allowed
        output = DummyOutput(name="fake_input")
        self.assertEqual(AbstractOutput.SetState.OK, output.set_state(True))
        self.assertEqual(AbstractOutput.SetState.WAITING, output.set_state(False))
        self.assertTrue(output.state)

        # but too many changes isn't detectable if the .state property is used
        # but the state isn't changed from first allowed value (i.e. True)
        output = DummyOutput(name="fake_output")
        output.state = True
        output.state = False
        self.assertTrue(output.state)
