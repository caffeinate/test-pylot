'''
Created on 31 Jan 2019

@author: si
'''

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

        :returns: XXX TODO
        """
        raise NotImplementedError()

class AbstractOutput(AbstractDevice):
    def set_output(self, state):
        """
        Must be implemented by subclasses.

        :param: state (boolean)
        :returns: X_OK or X_WAITING or X_FAIL or X_NO_CHANGE
        """
        raise NotImplementedError()
