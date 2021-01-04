'''
Created on 25 Jan 2019

@author: si
'''
from .global_profile import BaseProfile
from pi_fly.actional.dummy import DummyActional
from pi_fly.actional.solar_thermal import SolarThermal
from pi_fly.devices.dummy import DummyInput, DummyOutput
from pi_fly.devices.gpio_relay import GpioRelay


class Profile(BaseProfile):
    DEBUG = True
    HTTP_PORT = 8181
    SQLALCHEMY_DATABASE_URI = "sqlite:////Users/si/Documents/Scratch/sensors.db"
    fake_input_0 = DummyInput(name="fake_input_0")
    fake_input_1 = DummyInput(name="fake_input_1")
    INPUT_DEVICES = [fake_input_0,
                     fake_input_1
                     ]
    the_output_0 = DummyOutput(name="fake_output_0")
    the_output_1 = DummyOutput(name="fake_output_1")
    solar_pump = GpioRelay(name="solar_pump",
                           gpio_number=23,
                           min_switching_time=4.5,  # seconds
                           set_state_on_start=False,
                           log_to_stdout=True,
                           )
    OUTPUT_DEVICES = [the_output_0,
                      the_output_1,
                      solar_pump,
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
        SolarThermal(name="solar_thermal",
                     hot_water_bottom="fake_input_0",
                     solar_collector="fake_input_1",
                     solar_pump=solar_pump,
                     log_to_stdout=True,
                     ),
    ]
