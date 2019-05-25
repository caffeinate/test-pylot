import os
import tempfile

from .global_config import BaseConfig
from pi_fly.actional.dummy import DummyActional
from pi_fly.devices.dummy import DummyInput, DummyOutput

class Config(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = None # replaced with instance var in __init__
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
         'sample_frequency': .2,
         'devices': INPUT_DEVICES,
        }
        ]
    ACTIONALS = [
                DummyActional(name="fake_actional_0",
                               sample_frequency=5,
                               my_input="fake_input",
                               my_output=the_output_0
                               ),
                DummyActional(name="fake_actional_1",
                               sample_frequency=3,
                               my_input="fake_input",
                               my_output=the_output_1
                               ),
        ]

    def __init__(self):
        self.DB_FD, self.DB_FILE = tempfile.mkstemp()
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///%s" % self.DB_FILE

    def drop_db(self):
        if self.DB_FILE:
            os.close(self.DB_FD)
            #print "deleting %s" % self.DB_FILE
            os.unlink(self.DB_FILE)
