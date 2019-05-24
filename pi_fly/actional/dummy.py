from pi_fly.actional.abstract import AbstractActional
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
        self.log("dummy action is running")
        if self.scoreboard:
            current_value = self.scoreboard.get_current_value(self.my_input)
            # reply by doubling the value
            self.scoreboard.update_value('actional_reply', current_value*2)

            # magic value to take a specific action on
            if current_value == 123:
                self.my_output.state = True

    def run_command(self, cmd_message):
        """
        Dummy Actional just says hello back on the comms channel. It doesn't do anything useful.
        """
        self.log(f"hello command {cmd_message}")
