import time

from pi_fly.actional.abstract import AbstractActional, CommandTemplate
from pi_fly.devices.abstract import AbstractOutput
from pi_fly.devices.gpio_relay import GpioRelay


class SolarThermal(AbstractActional):
    SAMPLE_FREQUENCY = 5.

    def __init__(self, **kwargs):
        """
        required kwargs-
          hot_water_bottom (str) from :class:`pi_fly.devices.one_wire_temperature.OneWireTemperature`
                      The temperature near the hot water tank's heating coil supplied by the
                      solar thermal.
          solar_collector (str) from :class:`pi_fly.devices.one_wire_temperature.OneWireTemperature`
                        The temperature on the solar collector's manifold.
          solar_pump (instance of :class:`DummyOutput` for testing or :class:`GpioRelay` for live)
                      on off relay switch to run the solar collector's water pump.
        """
        self.hot_water_bottom = kwargs.pop('hot_water_bottom')
        self.solar_collector = kwargs.pop('solar_collector')
        self.solar_pump = kwargs.pop('solar_pump')
        assert isinstance(self.hot_water_bottom, str)
        assert isinstance(self.solar_collector, str)

        super().__init__(**kwargs)

        if not isinstance(self.solar_pump, GpioRelay):
            self.log("Not using GpioRelay for output", level="WARNING")
            # it must at least be an output device
            assert issubclass(self.solar_pump.__class__, AbstractOutput)

        self.consecutive_failed_readings = 0

        # Run the pump when the temperature difference between solar collector
        # and hot water tank temperature exceeds this (in degrees C)
        self.activate_on_thermal_difference = 3.

        # the time() to run the pump until. This is set by manual command from the
        # user. 0 means not in command mode.
        self.run_pump_until = 0

    def _gather_input_readings(self):
        """
        :returns:  None if reading either sensor failed
                    (float, float) which is temperatures at (hot_water_bottom, solar_collector)
        """
        # TODO take time of reading into account
        try:
            hot_water_bottom = self.scoreboard.get_current_value(self.hot_water_bottom)[
                'value_float']
        except KeyError:
            # could do something if the input isn't yet available or if it disappeared
            hot_water_bottom = None

        try:
            solar_collector = self.scoreboard.get_current_value(self.solar_collector)['value_float']
        except KeyError:
            # could do something if the input isn't yet available or if it disappeared
            solar_collector = None

        if hot_water_bottom is None or solar_collector is None:
            msg = "Solar collect reading is {} and hot_water_bottom is {}"
            self.log(msg.format(solar_collector, hot_water_bottom), level="ERROR")
            return None
        else:
            return hot_water_bottom, solar_collector

    def actional_loop_actions(self):

        input_readings = self._gather_input_readings()

        if input_readings is None:
            self.consecutive_failed_readings += 1
            if self.consecutive_failed_readings > 3:
                msg = "consecutive_failed_readings={}".format(self.consecutive_failed_readings)
                self.log(msg, level="ERROR")
            return

        self.consecutive_failed_readings = 0
        hot_water_bottom, solar_collector = input_readings
        thermal_difference = solar_collector - hot_water_bottom

        if self.run_pump_until != 0:
            # User command to run the pump
            if self.run_pump_until > time.time():
                self.log("Manual pump run starts.")
                self.solar_pump.state = True
            else:
                self.log("Manual pump run ends.")
                self.solar_pump.state = False
                self.run_pump_until = 0

        elif solar_collector <= 1.:
            self.log("Freeze protection: running solar thermal pump.")
            self.solar_pump.state = True

        elif thermal_difference > self.activate_on_thermal_difference:
            self.log("Running solar thermal pump.")
            self.solar_pump.state = True

        elif self.solar_pump.state == True:
            self.log("Stopping solar thermal pump.")
            self.solar_pump.state = False

    def run_command(self, cmd_message):
        """
        Dummy Actional just says hello back on the comms channel. It doesn't do anything useful.
        """
        if cmd_message == 'run:5':
            self.run_pump_until = time.time() + 5
        elif cmd_message == 'run:60':
            self.run_pump_until = time.time() + 60
        else:
            self.log("Unknown command {}".format(cmd_message), level="ERROR")

    @property
    def available_commands(self):
        cts = [CommandTemplate(command='run:5',
                               description='Run the solar pump for 5 seconds'
                               ),
               CommandTemplate(command='run:60',
                               description='Run the solar pump for 60 seconds'
                               ),
               ]

        return cts
