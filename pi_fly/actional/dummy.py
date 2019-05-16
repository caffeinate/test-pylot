from pi_fly.actional.abstract import AbstractActional

class DummyActional(AbstractActional):
    SAMPLE_FREQUENCY = 0.5

    def actional_loop_actions(self):
        self.log("dummy action is running")

    def run_command(self, cmd_message):
        """
        Dummy Actional just says hello back on the comms channel. It doesn't do anything useful.
        """
        self.log(f"hello command {cmd_message}")
