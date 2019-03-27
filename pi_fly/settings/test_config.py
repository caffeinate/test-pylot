import os
import tempfile

from .global_config import BaseConfig
from pi_fly.devices.dummy import DummyInput, DummyOutput

class Config(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = None # replaced with instance var in __init__
    INPUT_DEVICES = [DummyInput(name="fake_input"),
                     ]
    OUTPUT_DEVICES = [DummyOutput(name="fake_output"),
                      ]
    DEVICES = INPUT_DEVICES + OUTPUT_DEVICES
    POLLING_LOOPS = [
        {'name': 'short_loop',
         'sample_frequency': .2,
         'devices': INPUT_DEVICES,
        }
        ]

    def __init__(self):
        self.DB_FD, self.DB_FILE = tempfile.mkstemp()
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///%s" % self.DB_FILE

    def drop_db(self):
        if self.DB_FILE:
            os.close(self.DB_FD)
            #print "deleting %s" % self.DB_FILE
            os.unlink(self.DB_FILE)
