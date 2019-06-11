'''
Created on 9 Jun 2019

@author: si
'''
import time

try:
    import RPi.GPIO as GPIO
except:
    # TODO deal with this
    pass

from .abstract import AbstractOutput

class GpioRelay(AbstractOutput):
    """
    Use the Raspberry Pi's general purpose input output to switch a relay.
    """
    def __init__(self, *args, **kwargs):
        """
        Switch a relay. Note the GPIO.output(self.gpio_number, GPIO.HIGH) is relay off.
        TODO add note about wiring the relay to confirm point about HIGH being off.

        Mandatory kwargs:
            'gpio_number' (int) e.g. int 25 is GPIO25 and is pin 22 on a Raspberry Pi B+ 
        Optional kwargs:
            'min_switching_time' (int) seconds minimum time between switches to protect devices
                        that don't like being turned on and off a lot. Users of this device should
                        really take care this is an additional envelope protection.
        """
        self.last_change = None
        self.current_state = None # None means undefined
        self.min_switching_time = kwargs.pop('min_switching_time', 1.)
        self.gpio_number = kwargs.pop('gpio_number')
        assert isinstance(self.gpio_number, int)

        # initiate the hardware
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.OUT)

        super(GpioRelay, self).__init__(*args, **kwargs)

    def set_state(self, state):
        now = time.time()
        if self.last_change is not None \
        and now-self.min_switching_time < self.last_change:
            # rapid switching not allowed by DummyOutput
            return AbstractOutput.SetState.WAITING

        if self.current_state == state:
            return AbstractOutput.SetState.NO_CHANGE

        self.log("Setting state to {}".format(state))
        self.last_change = now
        self.current_state = state

        if state:
            GPIO.output(self.gpio_number, GPIO.LOW)
        else:
            GPIO.output(self.gpio_number, GPIO.HIGH)

        return AbstractOutput.SetState.OK

    def get_state(self, force_read=False):
        return self.current_state
