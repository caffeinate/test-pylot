'''
Created on 25 Jan 2019

@author: si
'''
from .global_config import BaseConfig
from pi_fly.actional.dummy import DummyActional
from pi_fly.devices.dummy import DummyInput, DummyOutput

class Config(BaseConfig):
    DEBUG=True
    HTTP_PORT = 8181
    SQLALCHEMY_DATABASE_URI = "sqlite:////Users/si/Documents/Scratch/sensors.db"
    INPUT_DEVICES = [DummyInput(name="fake_input"),
                     ]
    the_output_0 = DummyOutput(name="fake_output_0")
    the_output_1 = DummyOutput(name="fake_output_1")
    OUTPUT_DEVICES = [the_output_0,
                      the_output_1,
                      ]
    DEVICES = INPUT_DEVICES + OUTPUT_DEVICES
    POLLING_LOOPS = [
        {'name': 'short_loop',
         'sample_frequency': 2,
         'devices': INPUT_DEVICES,
         'log_to_stdout': True,
        }
        ]
    ACTIONALS = [
                DummyActional(name="fake_actional_0",
                               sample_frequency=5,
                               my_input="fake_input",
                               my_output=the_output_0,
                               log_to_stdout=True
                               ),
                DummyActional(name="fake_actional_1",
                               sample_frequency=3,
                               my_input="fake_input",
                               my_output=the_output_1,
                               log_to_stdout=True
                               ),
        ]
