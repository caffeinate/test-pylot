'''
Created on 1 Feb 2019

@author: si
'''
from multiprocessing import Manager

WORK_AROUNG_PY34_BUG = True


class ScoreBoard:
    """
    Shared memory to hold values read from sensors.
    """

    def __init__(self):
        # manager shouldn't be serialised and the scoreboard is passed between processes so
        # don't keep it in instances.
        manager = Manager()
        # TODO - py3.8, maybe look at multiprocessing.managers.SharedMemoryManager
        self.shared_data = manager.dict()

    def update_value(self, device_name, values_read):
        """
        :param: device_name (str)
        :param: values_read (dict), whatever comes from that type of sensor
                        example: {'sensor_id': '28-0015231007ee',
                                  'value_type': 'temperature',
                                  'value_float': 15.377
                                  }
        """
        if WORK_AROUNG_PY34_BUG:
            # simplified - can't store previous values
            self.shared_data[device_name] = values_read
        else:
            msg = ("Change to not keep manager as self.manager means proxy object within a proxy "
                   "object no longer possible. Use the method detailed in paragraph starting .. "
                   "'If standard (non-proxy) list or dict objects are contained in a referent...' "
                   "from https://docs.python.org/3/library/multiprocessing.html#managers"
                   )
            raise NotImplementedError(f"TODO: {msg}")

            if device_name not in self.shared_data:
                self.shared_data[device_name] = self.manager.dict()

            self.shared_data[device_name]["previous_values"] = self.manager.list()

            # TODO, race condition if current value is appended to previous?
            # don't store previous for now.

            self.shared_data[device_name]["current_value"] = values_read

    def get_current_value(self, device_name):
        if WORK_AROUNG_PY34_BUG:
            return self.shared_data[device_name]
        else:
            return self.shared_data[device_name]["current_value"]

    def get_all_current_values(self):
        """
        Ideally, avoid a race condition by returning the lot.
        :returns list of (str, dict) (device_name, current_value).
                device_name will be a string, e.g. fake_0
                current_value will be a dict, e.g.
                {'sensor_id': None, 'value_type': 'time', 'value_float': 1550350895.377642}
        """
        out = []
        for device_name in self.shared_data.keys():
            try:
                if WORK_AROUNG_PY34_BUG:
                    out.append((device_name, self.shared_data[device_name]))
                else:
                    out.append((device_name, self.shared_data[device_name]["current_value"]))
            except:
                # device was removed or data malformed?
                pass

        return out
