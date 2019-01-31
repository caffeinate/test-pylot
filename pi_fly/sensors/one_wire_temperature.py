'''
Created on 31 Jan 2019

@author: si
'''
import os

from .abstract_sensor import AbstractSensor

class OneWireTemperature(AbstractSensor):
    def __init__(self, device_name, *args, **kwargs):
        super(OneWireTemperature, self).__init__(*args, **kwargs)
        self.device_id = device_name
        self.device_path = "/sys/bus/w1/devices/{}/w1_slave".format(device_name)

    def get_reading(self):
        """
        e.g.
        77 02 4b 46 7f ff 0c 10 d7 : crc=d7 YES
        77 02 4b 46 7f ff 0c 10 d7 t=39437
        """
        temp = None
        if not os.access(self.device_path, os.R_OK):
            self.log("Device {} not found".format(self.device_id), "ERROR")
        else:
            with open(self.device_path) as f:
                sd = f.readlines()
                if not sd[0].strip().endswith("YES") or 't=' not in sd[1]:
                    self.log("Can't read {} : {}".format(self.device_id, " : ".join(sd)))
                else:
                    parts = sd[1].strip().split('t=')
                    temp = float(parts[1])/1000.

        return {'sensor_id': self.device_id,
                'value_type': "temperature",
                'value_float': temp
                }
