'''
Created on 1 May 2019

@author: si
'''

class AbstractActional:
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
    def __init__(self, name, **kwargs):
        """
        :param: name (str) - how to reference this actional in logs etc.
        :param: **kwargs what ever inputs and outputs the subclass needs
        """
        self.name = name
        self.comms_channel = None
    
    def set_comms_channel(self, comms_channel):
        """
        :param: comms_channel instance of :class:`multiprocessing.Pipe`
        """
        self.comms_channel = comms_channel

    def __call__(self):
        """
        To be implemented by subclass, is run in a separate process, does not return.
        It probably watches the comms_channel for incoming commands or just
        does it's own thing
        """
        raise NotImplementedError("Should be implemented by subclass")
