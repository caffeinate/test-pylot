'''
Created on 31 Jan 2019

@author: si
'''

class AbstractSensor(object):
    def __init__(self, *args, **kwargs):
        self.log_to_stdout = True

    def log(self, msg, level="INFO"):
        # TODO wire this to top level's log
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))

    def get_reading(self):
        """
        Must be implemented by subclasses.

        :returns: XXX TODO
        """
        raise NotImplementedError()