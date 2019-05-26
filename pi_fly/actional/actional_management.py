'''
Created on 25 May 2019

@author: si
'''
from datetime import datetime
from multiprocessing import Process, Pipe
from multiprocessing.connection import wait

from pi_fly.actional.abstract import CommsMessage


def build_actional_processes(config, scoreboard):
    """
    Actionals each run in their own multiprocessing.Process. There is a pipe to each actional
    and a governor that watches all the pipes for messages from the Actionals.

    None of the Processes in the returned items have been started.

    :param: config dict. like config with `ACTIONALS` as list of instances with superclass of
            :class:`AbstractActional` probably a flask config object.

    :returns: tuple (Process, dict)
            'Process' is the governor process
            'dict' has key as the actionals' names and value is a dict. with 
                                                'process' (the actional's process)
                                                'comms' our end of the Pipe to the actional

            If there are no actionals in the config the Process will be None and the dict. will be
            empty.
    """
    actionals = {}

    if isinstance(config, dict):
        actionals_config = config['ACTIONALS']
    else:
        actionals_config = config.ACTIONALS

    if len(actionals_config) == 0:
        return {}

    for a in actionals_config:
        parent_conn, child_conn = Pipe()
        a.set_comms_channel(child_conn)
        a.set_scoreboard(scoreboard)
        p = Process(target=a)
        actionals[a.name] = {'process': p,
                             'comms': parent_conn,
                             }

    # hmmm, this might need some more thought. Shared dict. or governor as the proxy as one of the
    # reasons for processes is for restart if there is a problem. The actionals dict is being
    # passed pre-fork so will loose sync when processes are added and removed.
    return actionals

def governor_run_forever(actionals):
    """
    Read comms messages from actionals. At present, these are just log messages but this is
    expected to evolve to commands for other actionals later.

    :param actionals: (dict) from :function:`build_actional_processes`
    """
    # TODO pass a logger, inline func for now
    def log(msg, level="INFO", date_stamp=None):
        if date_stamp is None:
            date_stamp = datetime.utcnow()
        date_formatted = date_stamp.strftime("%Y-%m-%d %H:%M:%S")
        print("{} {}{}".format(date_formatted, level.ljust(10), msg))

    # see warning about loosing sync at end of build_actional_processes
    comms_set = {a['comms']: a_name for a_name, a in actionals.items()}
    # TODO what if an actional Proc dies. How will this handle error?
    while True:
        for a_comms in wait(comms_set.keys()):
            a_name = comms_set[a_comms]

            try:
                msg = a_comms.recv()
            except EOFError:
                log(f"Failed to read from {a_name}.", "ERROR")
                # TODO remove it outside of this loop
            else:
                if not isinstance(msg, CommsMessage):
                    m = "Skipping msg received from {} as in wrong format. Got {}"
                    log(m.format(a_name, str(msg)), "ERROR")
                elif msg.action == 'log':
                    l_msg, l_level = msg.message
                    log_msg = "({}) {}".format(a_name, l_msg)
                    log(log_msg, level=l_level, date_stamp=msg.date_stamp)
                else:
                    log("Unknown message type received by actional governor", "ERROR")
