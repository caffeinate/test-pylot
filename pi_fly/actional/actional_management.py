'''
Created on 25 May 2019

@author: si
'''
from multiprocessing import Process, Pipe
import time

# multiprocessing.connection.wait(object_list, timeout=None)

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
                                                'send' our end of the Pipe to the actional

            If there are no actionals in the config the Process will be None and the dict. will be
            empty.
    """
    actionals = {}

    if isinstance(config, dict):
        actionals_config = config['ACTIONALS']
    else:
        actionals_config = config.ACTIONALS

    if len(actionals_config) == 0:
        return None, {}

    for a in actionals_config:
        parent_conn, child_conn = Pipe()
        a.set_comms_channel(child_conn)
        a.set_scoreboard(scoreboard)
        p = Process(target=a)
        actionals[a.name] = {'process': p,
                             'send': parent_conn,
                             }

    # hmmm, this might need some more thought. Shared dict. or governor as the proxy as one of the
    # reasons for processes is for restart if there is a problem. The actionals dict is being
    # passed pre-fork so will loose sync.
    def governor_run_forever():
        while True:
            for a_name, a in actionals.items():
                print(f"hello {a_name}")
                time.sleep(2)

    governor_proc = Process(target=governor_run_forever)
    return governor_proc, actionals
