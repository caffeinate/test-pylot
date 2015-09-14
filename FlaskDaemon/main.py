'''
Created on 10 Sep 2015

@author: si
'''
import hashlib
import logging
import threading
import time

from flask import Flask, current_app
from werkzeug.serving import run_simple


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

class SimpleDaemonWorker(threading.Thread):
    """
    class SimpleDaemon runs in a thread
    """
    def __init__(self, task_id, lock, data):
        super(SimpleDaemonWorker, self).__init__()
        self.task_id = task_id
        self.shared_lock = lock
        self.shared_data = data
        self.threads_shutdown_signal = False

    def run(self):

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

            if self.threads_shutdown_signal:
                logger.debug("worker thread [%s] got shutdown" % self.task_id)
                return

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
        s = ""
        while(True):
            md5 = hashlib.md5(s).hexdigest()
            if md5[0:count] == str(ch) * count:
                return (ch, len(s))
            s += ch

class SimpleDaemon(Flask):
    """
    run a few threads that do something and return results to a shared_data
    area.
    go(..) and flask's own run(..) are run in separate threads.
    """
    def __init__(self, *args, **kwargs):
        super(SimpleDaemon, self).__init__(*args, **kwargs)
        self.shared_lock = threading.Lock()
        self.shared_data = {}
        self.tasks = []
        self.shutdown_after_tasks_count = 900 # after X tasks completed

    def start_workers(self, num_threads):

        self.tasks = [SimpleDaemonWorker(  i,
                                           self.shared_lock,
                                           self.shared_data
                                           )
                      for i in range(num_threads)
                      ]

        for t in self.tasks:
            t.start()

    def start_webserver(self):
        """
        Run websever in separate thread.
        """
        # Flask's run(..) uses werkzeug.serving.run_simple but doesn't expose
        # all arguments.
        webserver = BackgroundTask(self, '_start_webserver')
        webserver.setDaemon(True)
        webserver.start()

    def _start_webserver(self):
        run_simple('127.0.0.1', 5000, self, use_reloader=False, use_debugger=False)

    def run_forever(self):
        while True:
            time.sleep(2.0)

            self.shared_lock.acquire()

            c = reduce(lambda x, y: x+y, [len(v) for v in self.shared_data.values()])
            msg = "crypto_challenge completed %s times by %s workers"
            print msg % (c, len(self.shared_data))

            self.shared_lock.release()
            
            if c > self.shutdown_after_tasks_count:
                logger.info("signaling shutdown to worker threads")
                for t in self.tasks:
                    t.threads_shutdown_signal = True

                # return when all threads have finished
                for t in self.tasks:
                    t.join()
                logger.debug("SimpleDaemon returning")
                return

app = SimpleDaemon(__name__)

@app.route("/")
def hello():

    current_app.shared_lock.acquire()

    r = "Hello World!"
    for task_id, completed in current_app.shared_data.iteritems():
        r += " %s : %s" % (task_id, str(len(completed)))

    current_app.shared_lock.release()

    return r

app.start_workers(4)
app.start_webserver()
app.run_forever()


