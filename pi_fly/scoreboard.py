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

    def get_all_current_values(self):
        """
        Ideally, avoid a race condition by returning the lot.
        :returns list of (str, dict) (device_name, current_value).
                device_id will be a string, e.g. fake_0
                current_value will be a dict, e.g.
                {'sensor_id': None, 'value_type': 'time', 'value_float': 1550350895.377642}
        """
        out = []
        for device_id in self.shared_data.keys():
            try:
                out.append((device_id, self.shared_data[device_id]["current_value"]))
            except:
                # device was removed
                pass

        return out
