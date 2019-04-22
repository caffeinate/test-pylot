'''
Created on 31 Jan 2019

@author: si
'''
import time

from .abstract import AbstractSensor, AbstractOutput

class DummyInput(AbstractSensor):
    """
    Fake sensor for testing and development.
    """
    def __init__(self, *args, **kwargs):
        super(DummyInput, self).__init__(*args, **kwargs)

    def get_reading(self):
        """
        return the unix epoc time
        """
        return {'sensor_id': None,
                'value_type': "time",
                'value_float': time.time()
                }

class DummyOutput(AbstractOutput):

    def __init__(self, *args, **kwargs):
        super(DummyOutput, self).__init__(*args, **kwargs)
        self.last_change = None
        self.current_state = None # None means undefined

    def set_state(self, state):
        """
        The dummy output device is an on/off switch that allows one change per
        10 milliseconds.

        :param: state (boolean) value to set on output device.
                        for on/off devices this will be a boolean.
        :returns: AbstractOutput.SetState
        """
        min_switching_time = 0.01 # seconds
        now = time.time()

        if self.last_change is not None \
        and now-min_switching_time < self.last_change:
            # rapid switching not allowed by DummyOutput
            return AbstractOutput.SetState.WAITING

        if self.current_state == state:
            return AbstractOutput.SetState.NO_CHANGE

        self.last_change = now
        self.current_state = state
        return AbstractOutput.SetState.OK

    def get_state(self, force_read=False):
        return self.current_state
