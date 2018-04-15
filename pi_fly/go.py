'''
Created on 14 Apr 2018

@author: si
'''
import os
import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Sensor

Base = declarative_base()

class AbstractSensorDecode(object):
    def __init__(self, *args, **kwargs):
        self.log_to_stdout = True

    def log(self, msg, level="INFO"):
        # TODO wire this to top level's log
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))


class OneWireTemperatureDecode(AbstractSensorDecode):
    def __init__(self, device_name, *args, **kwargs):
        super(OneWireTemperatureDecode, self).__init__(*args, **kwargs)
        self.device_id = device_name
        self.device_path = "/sys/bus/w1/devices/{}/w1_slave".format(device_name)

    def get_reading(self):
        temp = None
        """
        e.g.
        77 02 4b 46 7f ff 0c 10 d7 : crc=d7 YES
        77 02 4b 46 7f ff 0c 10 d7 t=39437
        """
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


class SensorsDb(object):
    def __init__(self, db_dsn):
        """
        :param: db_dsn (str) for sqlalchemy. e.g. 'sqlite:////data/sensors.db'
        """
        self.sensors_db = db_dsn
        self.log_to_stdout = True
        self._db_session = None
        self.sample_frequency = 10 #5*60 # in seconds
        self.sensors = []
    
    def add_sensor(self, s):
        assert isinstance(s, AbstractSensorDecode)
        self.sensors.append(s)

    def log(self, msg, level="INFO"):
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))

    def create_db(self):
        engine = create_engine(self.sensors_db)
    
        if not os.access(self.sensors_db, os.R_OK):
            self.log("Creating new DB {}".format(self.sensors_db))
            Base.metadata.create_all(engine)
    
    @property
    def db_session(self):
        if self._db_session is None:
            engine = create_engine(self.sensors_db)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            self._db_session = DBSession()
        return self._db_session
    
    def store_reading(self, reading):
        """
        :param: reading (dict) matching keys see :class:`Sensor` model 
        """
        r = Sensor(**reading)
        self.db_session.add(r)
        self.db_session.commit()

    def run_forever(self):
        
        self.log("Running...")
        
        while True:
            sampling_start_time = time.time()
            
            for sensor in self.sensors:
                r = sensor.get_reading()
                self.log("Reading: {device},{value_type},{value_float}".format(**r))
                self.store_reading(r)

            wait_for = self.sample_frequency - (time.time() - sampling_start_time)
            if wait_for < 0:
                self.log("Couldn't keep up with sampling", "WARNING")
            else:
                time.sleep(wait_for)
        

if __name__ == '__main__':
    sensors_db = 'sqlite:////data/sensors.db'
    sdb = SensorsDb(sensors_db)
    sdb.create_db()

    sdb.add_sensor(OneWireTemperatureDecode("28-0015231007ee"))
    sdb.add_sensor(OneWireTemperatureDecode("28-021571be4cff"))
    
    sdb.run_forever()
