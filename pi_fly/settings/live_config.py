from .global_config import BaseConfig
from pi_fly.devices.dummy import DummyOutput
from pi_fly.devices.one_wire_temperature import OneWireTemperature

class Config(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = "sqlite:////data/sensors.db"
    input_devices = [
        OneWireTemperature("28-0015231007ee",
                           name="hot_water_top",
                           description="top of hot water tank"),
        OneWireTemperature("28-021571be4cff",
                           name="roof",
                           description="dangling on roof"),
        OneWireTemperature("28-0517c16726ff",
                           name="solar_collector",
                           description="solar collector from 2018-11-13, loft before"),
        OneWireTemperature("28-0517c1599eff",
                           name="house_inside_landing",
                           description="landing"),
        OneWireTemperature("28-041783906fff",
                           name="hot_water_bottom",
                           description="bottom of tank"),
                     ]
    output_devices = [DummyOutput(name="fake_output"),
                      ]
    DEVICES = input_devices + output_devices
    POLLING_LOOPS = [
        {'name': 'one_wire_general_bus',
         'sample_frequency': 20,
         'devices': input_devices,
        }
        ]
