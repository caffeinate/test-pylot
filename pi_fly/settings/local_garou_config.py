'''
Created on 25 Jan 2019

@author: si
'''
from .global_config import BaseConfig
from pi_fly.sensors.dummy_sensor import Dummy

class Config(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/si/Desktop/sensors.db"
    SENSORS = [
        {'loop_name': 'short_loop',
         'minimum_cycle': 2., 
         'devices': [Dummy(),
                     ],
        }
        ]
