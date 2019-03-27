'''
Created on 25 Jan 2019

@author: si
'''
from .global_config import BaseConfig
from pi_fly.devices.dummy import DummyInput, DummyOutput

class Config(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = "sqlite:////Users/si/Documents/Scratch/sensors.db"
    input_devices = [DummyInput(name="fake_input"),
                     ]
    output_devices = [DummyOutput(name="fake_output"),
                      ]
    DEVICES = input_devices + output_devices
    POLLING_LOOPS = [
        {'name': 'short_loop',
         'sample_frequency': .2,
         'devices': input_devices,
        }
        ]
