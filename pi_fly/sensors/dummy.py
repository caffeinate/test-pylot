'''
Created on 31 Jan 2019

@author: si
'''
import time

from .abstract_sensor import AbstractSensor

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

class DummyOutput:
    pass
