'''
Created on 1 Feb 2019

@author: si
'''
from multiprocessing import Manager

class ScoreBoard:
    """
    Shared memory to hold values read from sensors.
    """
    def __init__(self):
        self.manager = Manager()
        self.shared_data = self.manager.dict()

    def update_value(self, device_name, values_read):
        """
        :param: device_name (str)
        :param: values_read (dict)
        """
        if device_name not in self.shared_data:
            self.shared_data[device_name] = self.manager.dict()
            self.shared_data[device_name]["previous_values"] = \
                self.manager.list()

        # TODO, race condition if current value is appended to previous?
        # don't store previous for now.

        self.shared_data[device_name]["current_value"] = values_read
    
    def get_current_value(self, device_name):
        return self.shared_data[device_name]["current_value"]
