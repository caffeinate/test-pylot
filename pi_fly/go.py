'''
Created on 14 Apr 2018

@author: si
'''
import os
import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pi_fly.model import Sensor, Base
from pi_fly.sensors.abstract_sensor import AbstractSensor

class SensorsDb(object):
    def __init__(self, db_dsn):
        """
        :param: db_dsn (str) for sqlalchemy. e.g. 'sqlite:////data/sensors.db'
        """
        self.sensors_db = db_dsn
        self.log_to_stdout = True
        self._db_session = None
        self.sample_frequency = 5*60 # in seconds
        self.sensors = []
    
    def add_sensor(self, s):
        assert isinstance(s, AbstractSensor)
        self.sensors.append(s)

    def log(self, msg, level="INFO"):
        if self.log_to_stdout:
            print("{}{}".format(level.ljust(10), msg))

    def create_db(self):
        engine = create_engine(self.sensors_db)
    
        if not os.access(self.sensors_db, os.R_OK):
            self.log("Creating new DB {}".format(self.sensors_db))
        # just update tables
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
                self.log("Reading: {sensor_id},{value_type},{value_float}".format(**r))
                self.store_reading(r)

            wait_for = self.sample_frequency - (time.time() - sampling_start_time)
            if wait_for < 0:
                self.log("Couldn't keep up with sampling", "WARNING")
            else:
                time.sleep(wait_for)
        

if __name__ == '__main__':
    # TODO - take from settings file
    sensors_db = 'sqlite:////data/sensors.db'
    sdb = SensorsDb(sensors_db)
    sdb.create_db()

    sdb.add_sensor(OneWireTemperatureDecode("28-0015231007ee")) # top of hot water tank
    sdb.add_sensor(OneWireTemperatureDecode("28-021571be4cff")) # dangling on roof
    sdb.add_sensor(OneWireTemperatureDecode("28-0517c16726ff")) # solar collector from 2018-11-13, loft before
    sdb.add_sensor(OneWireTemperatureDecode("28-0517c1599eff")) # landing
    sdb.add_sensor(OneWireTemperatureDecode("28-041783906fff")) # bottom of tank
    sdb.run_forever()

