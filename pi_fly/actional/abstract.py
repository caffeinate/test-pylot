'''
Created on 1 May 2019

@author: si
'''
from collections import namedtuple
from datetime import datetime

from pi_fly.polling_loop import AbstractPollingLoop

# only 'action' can be 'command'|'log', 'message' is mixed. Up to receiver.
# is action is 'command' and message == 'terminate' the process will end at end of next loop
CommsMessage = namedtuple('CommsMessage', ['action', 'message', 'date_stamp'])
CommsMessage.__new__.__defaults__ = (None,) * len(CommsMessage._fields)

class AbstractActional(AbstractPollingLoop):
    """
    Abstract class to take an action based on inputs.

    The 'action' is probably via a subclass of :class:`AbstractOutput` and the inputs are probably
    subclasses of :class:`AbstractSensor`.

    Each Actional is instantiated in it's own Process (see multiprocessing.Process) and is
    connected to the rest of the system by an instance of :class:`scoreboard.Scoreboard` and
    a communications channel which is a multiprocessing.Pipe.

    Input values (i.e. sensor readings) are expected to be taken from the scoreboard and not
    directly from the sensors. This is indicated through passing a string naming the sensor
    to the constructor rather than an instance of :class:`AbstractSensor`.

    Actionals can write to the scoreboard (statistics, current action, last action etc.).

    The communications channel is used to (a) receive commands (e.g. a change of parameters or a
    mode of operation commanded by a user), (b) reply when a command has been actioned and
    (c) send log messages - because each Actional runs within an isolated process it makes sense
    for the parent process to collate log messages before outputting them. 
    """
    def __init__(self, **kwargs):
        """
        possible kwargs-
            everything supported by :class:`AbstractPollingLoop` base class.
            and what ever inputs and outputs the subclass needs
        """
        # scoreboard is added later
        super().__init__(None, **kwargs)
        self.comms_channel = None
        self.polling_timeout = self.sample_frequency / 2  # how long to wait for incoming messages

    def set_scoreboard(self, scoreboard):
        """
        Other subclasses of :class:`AbstractPollingLoop` set the scoreboard in the constructor
        but actionals are inititated in settings where the scoreboard isn't available so it's
        set later using this method.
        """
        self.scoreboard = scoreboard

    def set_comms_channel(self, comms_channel):
        """
        :param: comms_channel instance of :class:`multiprocessing.Pipe`
        """
        self.comms_channel = comms_channel

    def log(self, msg, level="INFO"):
        if self.comms_channel:
            # log messages are sent back to the parent via the comms channel
            date_stamp = datetime.utcnow()
            cm = CommsMessage(action="log", message=(msg, level), date_stamp=date_stamp)
            self.comms_channel.send(cm)
        else:
            # try stdout/whatever has been set locally
            super().log(msg, level)

    def loop_actions(self):
        """
        What to do each time the loop is run.
        """
        # Check the comms channel for messages for the subclass. Messages from the subclass
        # are read by the governor process (see :function:`actional_manage.governor_run_forever`)
        if self.comms_channel.poll(self.polling_timeout):
            msg = self.comms_channel.recv()
            if not isinstance(msg, CommsMessage):
                m = "Skipping msg received as in wrong format. Should be CommsMessage. Got {}"
                self.log(m.format(str(msg)))
            elif msg.action == 'command':
                if msg.message == 'terminate':
                    self.terminate_now = True
                else:
                    self.run_command(msg.message)
            else:
                self.log("Unknown message type received on comms channel")

        # run subclass's actions.
        self.actional_loop_actions()

    def actional_loop_actions(self):
        """
        To be implemented by subclass. This method is run once per loop and contains actional
        logic and actions not including checking the comms channel as that is done by
        :method:`AbstractActional.loop_actions`

        Receiving messages on the comms channel will slightly alter how regular this method will be
        called but it will typically be every  (1 / AbstractPollingLoop.sample_frequency) seconds.
        """
        raise NotImplementedError("Should be implemented by subclass")

    def run_command(self, cmd_message):
        """
        To be implemented by subclass.
        CommsMessage's received on the comms pipe where type is 'command' are given to
        this method. The subclass is expected to use this to set an internal state
        or return a value (on the comms channel or via scoreboard).

        cmd_message (mixed) the value of CommsMessage.message as passed through the comms channel
                    to this actional.
        """
        raise NotImplementedError("Should be implemented by subclass")
