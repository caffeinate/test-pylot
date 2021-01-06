from datetime import datetime, timedelta
import time

from pi_fly.actional.abstract import AbstractActional, CommandTemplate, CommsMessage
from pi_fly.devices.dummy import DummyOutput


class DummyActional(AbstractActional):
    SAMPLE_FREQUENCY = 0.5

    def __init__(self, **kwargs):
        """
        required kwargs-
          my_input (str) with name of input device on scoreboard
          my_output (instance of :class:`DummyOutput`)
        """
        self.my_input = kwargs.pop('my_input')
        self.my_output = kwargs.pop('my_output')
        assert isinstance(self.my_input, str)
        assert isinstance(self.my_output, DummyOutput)

        super().__init__(**kwargs)

    def actional_loop_actions(self):
        self.log("dummy actional ({}) is running".format(self.name))
        if self.scoreboard:
            try:
                current_value = self.scoreboard.get_current_value(self.my_input)
            except KeyError:
                # could do something if the input isn't yet available or if it disappeared
                return

            # reply by doubling the value
            self.scoreboard.update_value('actional_reply', current_value['value_float'] * 2)

            # magic value to take a specific action on
            if current_value['value_float'] == 123:
                # number of switches per second is rate limited so just wait until set
                self.my_output.state = True
                while self.my_output.state != True:
                    time.sleep(0.01)
                    self.my_output.state = True

    def run_command(self, cmd_message):
        """
        Dummy Actional just says hello back on the comms channel. It doesn't do anything useful.
        """
        if cmd_message == 'hello':
            self.log("hello command {}".format(cmd_message))

        elif cmd_message == 'send_event':
            event_start = datetime.utcnow()
            event_end = event_start + timedelta(minutes=1)
            self.send_event('example event', event_start, event_end)

            self.log("example event sent")

        else:
            self.log("Unknown command {}".format(cmd_message), level="ERROR")

    @property
    def available_commands(self):
        cmds = [CommandTemplate(command='hello',
                                description='Log "hello command hello"'
                                ),
                CommandTemplate(command='send_event',
                                description='Send an event to the governor'
                                ),
                ]
        return cmds
