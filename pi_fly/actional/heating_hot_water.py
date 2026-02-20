from datetime import datetime
from enum import Enum
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pi_fly.actional.abstract import AbstractActional, CommandTemplate
from pi_fly.devices.abstract import AbstractOutput
from pi_fly.devices.gpio_relay import GpioRelay
from pi_fly.model import Base, Event


class BoilerMode(Enum):
    HEATING = "heating"
    HOTWATER = "hotwater"


class HeatingHotWater(AbstractActional):
    """
    Control a boiler with one relay for hot water and one for central heating. My boiler runs more
    efficiently if these are used mutually exclusively.
    """

    # check every 30 seconds
    # this is also how often manual commands are checked
    SAMPLE_FREQUENCY = 30

    def __init__(self, **kwargs):
        """
        required kwargs-
          db_dsn (str) - sqlalchemy connection string to access to DB. Needed to determine how much
                      time has been spent running hotwater and heating that day.
          hot_water_top (str) from :class:`pi_fly.devices.one_wire_temperature.OneWireTemperature`
                      The temperature near the hot water tank's outlet.
          house_inside_landing (str) from :class:`pi_fly.devices.one_wire_temperature.OneWireTemperature`
                        The temperature in the house.
          central_heating (instance of :class:`DummyOutput` for testing or :class:`GpioRelay` for live)
                      on off relay switch to run the boiler to heat the radiators.
          hot_water (instance of :class:`DummyOutput` for testing or :class:`GpioRelay` for live)
                      on off relay switch to run the boiler to heat the water in the tank.
        """
        self.sensors_db_dsn = kwargs.pop("db_dsn")
        self._db_session = None

        self.hot_water_top = kwargs.pop("hot_water_top")
        self.house_inside_landing = kwargs.pop("house_inside_landing")

        # relays to turn on the boiler's heating demand or hotwater demand
        self.boiler_control_switch = {
            BoilerMode.HEATING: kwargs.pop("central_heating"),
            BoilerMode.HOTWATER: kwargs.pop("hot_water"),
        }

        assert isinstance(self.hot_water_top, str)
        assert isinstance(self.house_inside_landing, str)

        super().__init__(**kwargs)

        for label, device in [
            ("heating", self.boiler_control_switch[BoilerMode.HEATING]),
            ("hotwater", self.boiler_control_switch[BoilerMode.HOTWATER]),
        ]:
            if not isinstance(device, GpioRelay):
                self.log(f"Not using GpioRelay for {label} output", level="WARNING")
                # it must at least be an output device
                assert issubclass(device.__class__, AbstractOutput)

        self.consecutive_failed_readings = 0

        # the time() to run xx until. This is set by manual command from the
        # user. 0 means not in command mode.
        self.run_until = {
            BoilerMode.HEATING: 0,
            BoilerMode.HOTWATER: 0,
        }

        # a pump event
        self.boiler_start = {
            BoilerMode.HEATING: None,
            BoilerMode.HOTWATER: None,
        }

    @property
    def db_session(self):
        if self._db_session is None:
            engine = create_engine(self.sensors_db_dsn)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            self._db_session = DBSession()
        return self._db_session

    def _gather_input_readings(self):
        """
        :returns:  dict with keys-
            - 'hot_water_top' : (float or None) - temperature degrees
            - 'house_inside_landing' : (float or None) - temperature degrees
            - 'hotwater_time' : (float or None) - seconds running in pervious 24 hr
            - 'heating_time' : (float or None) - seconds running in pervious 24 hr

            None for any value not available
        """
        # TODO take time of reading into account
        try:
            hot_water_top = self.scoreboard.get_current_value(self.hot_water_top)["value_float"]
        except KeyError:
            hot_water_top = None

        try:
            house_inside_landing = self.scoreboard.get_current_value(self.house_inside_landing)[
                "value_float"
            ]
        except KeyError:
            house_inside_landing = None

        r = {
            "hot_water_top": hot_water_top,
            "house_inside_landing": house_inside_landing,
            "hotwater_time": 0,  # TODO
            "heating_time": 0,  # TODO
        }

        return r

    def _start_boiler(self, boiler_mode):
        """
        @param boiler_mode: (BoilerMode)
        """
        assert boiler_mode in self.boiler_control_switch

        # flick gpio relay
        self.boiler_control_switch[boiler_mode].state = True

        if self.boiler_start[boiler_mode] is None:
            self.boiler_start[boiler_mode] = datetime.utcnow()

    def _stop_boiler(self, boiler_mode):
        """
        @param boiler_mode: (BoilerMode)
        """
        assert boiler_mode in self.boiler_control_switch

        # flick gpio relay
        self.boiler_control_switch[boiler_mode].state = False
        boiler_start = self.boiler_start[boiler_mode]
        self.send_event(f"{boiler_mode.value} running", boiler_start, datetime.utcnow())
        self.boiler_start[boiler_mode] = None

    def actional_loop_actions(self):
        for boiler_mode, run_util in self.run_until.items():
            if run_util != 0:
                if run_util > time.time():
                    self.log(f"Manual run for {boiler_mode} starts.")
                    self._start_boiler(boiler_mode=boiler_mode)
                else:
                    self.log(f"Manual run for {boiler_mode} ends.")
                    self._stop_boiler(boiler_mode=boiler_mode)
                    self.run_until[boiler_mode] = 0

        input_readings = self._gather_input_readings()

        if any([v is None for v in input_readings.values()]):
            self.consecutive_failed_readings += 1
            if self.consecutive_failed_readings > 3:
                msg = (
                    f"consecutive_failed_readings={self.consecutive_failed_readings} "
                    f": {input_readings}"
                )
                self.log(msg, level="ERROR")
            return

        self.consecutive_failed_readings = 0

    def run_command(self, cmd_message):
        """
        Dummy Actional just says hello back on the comms channel. It doesn't do anything useful.
        """
        if cmd_message == "heating:20":
            self.run_until[BoilerMode.HEATING] = time.time() + (20 * 60)
        elif cmd_message == "hotwater:20":
            self.run_until[BoilerMode.HOTWATER] = time.time() + (20 * 60)
        else:
            self.log("Unknown command {}".format(cmd_message), level="ERROR")

    @property
    def available_commands(self):
        cts = [
            CommandTemplate(command="heating:20", description="Run the heating for 20 minutes"),
            CommandTemplate(command="hotwater:20", description="Run the hot water for 20 minutes"),
        ]

        return cts
