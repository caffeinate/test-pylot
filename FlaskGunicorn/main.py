'''
Created on 10 Sep 2015

@author: si
'''
from __future__ import unicode_literals

import hashlib
import multiprocessing
import threading

import gunicorn.app.base
from gunicorn.six import iteritems

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


#----------------------------
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
#----------------------------

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
    def __init__(self):
        pass

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

class SimpleDaemon(object):
    """
    run a few threads that do something and return results to a shared area
    """
    def __init__(self):
        pass

    def go(self, num_threads):
        hex_chars = self._hex_chars(num_threads)

        tasks = [BackgroundTask(SimpleDaemonWorker(), 'crypto_challenge', [ch,4])
                 for ch in hex_chars
                 ]

        for t in tasks:
            t.start()

        # return when all threads have finished
        for t in tasks:
            t.join()
        logger.debug("SimpleDaemon returning")

    def _hex_chars(self, n):
        """
        @param n: length required
        @return: string of hex characters
        """
        hex_chars = '0123456789abcdef'
        while n > len(hex_chars):
            hex_chars += hex_chars
        hex_chars = hex_chars[0:n]
        return hex_chars


sd = BackgroundTask(SimpleDaemon(), 'go', [4,])
sd.start()

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('127.0.0.1', '8080'),
        'workers': number_of_workers(),
    }
    logger.debug("StandaloneApplication running")
    StandaloneApplication(app, options).run()