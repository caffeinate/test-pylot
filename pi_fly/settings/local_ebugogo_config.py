'''
Created on 25 Jan 2019

@author: si
'''
from .global_config import BaseConfig
from pi_fly.devices.dummy import DummyInput, DummyOutput

class Config(BaseConfig):
    DEBUG=True
    HTTP_PORT = 8181
    SQLALCHEMY_DATABASE_URI = "sqlite:////Users/si/Documents/Scratch/sensors.db"
    INPUT_DEVICES = [DummyInput(name="fake_input"),
                     ]
    OUTPUT_DEVICES = [DummyOutput(name="fake_output"),
                      ]
    DEVICES = INPUT_DEVICES + OUTPUT_DEVICES
    POLLING_LOOPS = [
        {'name': 'short_loop',
         'sample_frequency': .2,
         'devices': INPUT_DEVICES,
         'log_to_stdout': True,
        }
        ]
