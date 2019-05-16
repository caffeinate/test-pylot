from pi_fly.actional.abstract import AbstractActional

class DummyActional(AbstractActional):
    SAMPLE_FREQUENCY = 0.5

    def __call__(self):

        while True:
            print("polling")
            if self.comms_channel.poll(2.):
                msg = self.comms_channel.recv()
                print(f"got {msg}")
                self.comms_channel.send("hi there")
                return
