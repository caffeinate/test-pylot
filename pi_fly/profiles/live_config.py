from .global_config import BaseConfig
from pi_fly.actional.solar_thermal import SolarThermal
from pi_fly.devices.gpio_relay import GpioRelay
from pi_fly.devices.one_wire_temperature import OneWireTemperature

class Config(BaseConfig):
    DEBUG=True
    HTTP_PORT = 80
    SQLALCHEMY_DATABASE_URI = "sqlite:////data/sensors.db"
    NON_SOLAR_INPUT_DEVICES = [
        OneWireTemperature("28-0015231007ee",
                           name="hot_water_top",
                           description="top of hot water tank"),
        OneWireTemperature("28-021571be4cff",
                           name="roof",
                           description="dangling on roof"),
        OneWireTemperature("28-0517c1599eff",
                           name="house_inside_landing",
                           description="landing"),
        OneWireTemperature("28-041783906fff",
                           name="hot_water_bottom",
                           description="bottom of tank"),
                    ]
    SOLAR_INPUT_DEVICES = [
        OneWireTemperature("28-0517c16726ff",
                           name="solar_collector",
                           description="solar collector from 2018-11-13, loft before"),
                    ]

    solar_pump = GpioRelay(name="solar_pump",
                           gpio_number=23,
                           min_switching_time=4.5, # seconds
                           set_state_on_start=False,
                           log_to_stdout=True,
                           )
    INPUT_DEVICES = NON_SOLAR_INPUT_DEVICES + SOLAR_INPUT_DEVICES
    OUTPUT_DEVICES = [solar_pump,
                      ]
    DEVICES = INPUT_DEVICES + OUTPUT_DEVICES
    POLLING_LOOPS = [
        {'name': 'one_wire_general_bus',
         'sample_frequency': 20,
         'devices': NON_SOLAR_INPUT_DEVICES,
        },
        {'name': 'one_wire_general_bus',
         'sample_frequency': 5,
         'devices': SOLAR_INPUT_DEVICES,
        }
        ]
    ACTIONALS = [
                SolarThermal(name="solar_thermal",
                               hot_water_bottom="hot_water_bottom",
                               solar_collector="solar_collector",
                               solar_pump=solar_pump,
                               log_to_stdout=True,
                               ),
                ]
