'''
Created on 10 Sep 2015

@author: si
'''

from flask import Flask, current_app
import hashlib

import threading
import time


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

CHALLENGE_COMPLEXITY = 4

class BackgroundTask(threading.Thread):
    """
    Run an object in a thread.
    """
    def __init__(self, obj, method_name, method_args=[], method_kwargs={}):
        """
        @param obj: Object to run
        @param method: string. Name of class to run
        @param method_args list. to pass to method
        @param method_kwargs dict. to pass to method
        """
        super(BackgroundTask, self).__init__()
        self.obj = obj
        self.method_name = method_name
        self.method_args = method_args
        self.method_kwargs = method_kwargs

    def run(self):
        method = getattr(self.obj, self.method_name)
        command_return = method(*self.method_args, **self.method_kwargs)
        logger.debug("BackgroundTask returning")

class SimpleDaemonWorker(object):
    """
    class SimpleDaemon runs in a thread
    """
    def __init__(self, task_id, lock, data):
        self.task_id = task_id
        self.shared_lock = lock
        self.shared_data = data

    def run_forever(self):

        # starting point
        counter = self.task_id
        while True:
            counter = counter % 16
            next_char = hex(counter)[-1]
            ch, reps = self.crypto_challenge(next_char, CHALLENGE_COMPLEXITY)
            self.shared_lock.acquire()

            if self.task_id not in self.shared_data:
                self.shared_data[self.task_id] = []
            self.shared_data[self.task_id].append((ch, reps))

            self.shared_lock.release()
            counter += 1

    def crypto_challenge(self, ch, count):
        """
        @param ch: ascii character found in an md5sum

        return an int which is the length of a string composed of 'ch'
        which has the md5sum starting with count number of 'ch' 

        e.g.
        >>> crypto_challenge('a',3)
        27

        [si@buru ~]$ echo -n aaaaaaaaaaaaaaaaaaaaaaaaaaa | md5sum
        aaab9c59a88bf0bdfcb170546c5459d6  -
        [si@buru ~]$ 

        inspired by the bitcoin mining algorithm. 
        """
        s=""
        while(True):
            md5 = hashlib.md5(s).hexdigest()
            if md5[0:count] == str(ch) * count:
                return (ch, len(s))
            s+=ch 

class SimpleDaemon(Flask):
    """
    run a few threads that do something and return results to a shared area
    """
    def __init__(self, *args, **kwargs):
        super(SimpleDaemon, self).__init__(*args, **kwargs)
        self.shared_lock = threading.Lock()
        self.shared_data = {}

    def start_workers(self, num_threads):

        daemon_thread_count = 3
        tasks = [BackgroundTask(SimpleDaemonWorker(i,
                                                   self.shared_lock,
                                                   self.shared_data
                                                   ),
                               'run_forever'
                               )
                 for i in range(daemon_thread_count)
                 ]

        for t in tasks:
            t.start()

        #self.run(debug=True, use_reloader=False)

    def go(self):
        while True:
            time.sleep(3.0)
            print self.shared_data

        # return when all threads have finished
        for t in tasks:
            t.join()
        logger.debug("SimpleDaemon returning")


app = SimpleDaemon(__name__)

@app.route("/")
def hello():
    r = "Hello World!"
    for task_id, completed in current_app.shared_data.iteritems():
        r += " %s : %s" % (task_id, str(len(completed)))
    return r

app.start_workers(4)

sd = BackgroundTask(app, 'run', [], {'debug':True, 'use_reloader':False})
sd.start()

app.go()


