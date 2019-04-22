'''
Created on 31 Jan 2019

@author: si
'''
from enum import Enum

class AbstractDevice:
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.log_to_stdout = kwargs.pop('log_to_stdout', False)
        self.description = kwargs.pop('description', None)

    def log(self, msg, level="INFO"):
        # TODO wire this to top level's log
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))

class AbstractSensor(AbstractDevice):
    def get_reading(self):
        """
        Must be implemented by subclasses.

        :returns: (dict) with keys-
                'sensor_id' (str) (optional), internal id, not the 'name'
                'value_type' (str) e.g. "time", "temperature"
                'value_float' (float) value from the sensor
                  note other 'value_*' may be implemented
        """
        raise NotImplementedError()

class AbstractOutput(AbstractDevice):

    class SetState(Enum):
        OK = 0
        NO_CHANGE = 1
        WAITING = 2 # output device has been updated too frequently and refuses change
        FAIL = 3

    def __init__(self, *args, **kwargs):
        """
        kwargs in addition to those passed to :class:`AbstractDevice`
            set_state_on_start (mixed) call set state with this value when subclass is
                                        initiated.
        """
        super(AbstractOutput, self).__init__(*args, **kwargs)
        self.s = kwargs.pop('set_state_on_start', False)

    def set_state(self, state):
        """
        Must be implemented by subclasses.

        :param: state (mixed) value to set on output device.
                        for on/off devices this will be a boolean.
        :returns: AbstractOutput.SetState
        """
        raise NotImplementedError()

    def get_state(self, force_read=False):
        """
        :param force_read (boolean) if cached state can be used or if device should check
                value by reading from output device.
        :returns: (mixed) current value of output.
        """
        raise NotImplementedError()

    state = property(fget=lambda self: self.get_state(force_read=False),
                     fset=lambda self, state: self.set_state(state))
