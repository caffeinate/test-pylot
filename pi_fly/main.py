'''
Run web view with gunicorn

Created on 22 Apr 2018

@author: si
'''
# from __future__ import unicode_literals
from multiprocessing import Manager, Process
import sys
import time

import gunicorn.app.base
from gunicorn.six import iteritems

from pi_fly.web_view import create_app

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

    if len(sys.argv) != 2:
        msg = "usage: python main.py <settings label>\n"
        sys.stderr.write(msg)
        sys.exit(-1)
    
    def _counter(shared_memory):
        
        while True:
            shared_memory['counter'] += 1
            time.sleep(2)

    app = create_app('settings.%s_config.Config' % sys.argv[1])
    app.manager = Manager()
    app.shared_data = app.manager.dict()
    app.shared_data['counter'] = 0

    counter_proc = Process(target=_counter, args=(app.shared_data,))
    counter_proc.start()

    options = {
        'bind': '%s:%s' % ('0.0.0.0', app.config.get('HTTP_PORT', '80')),
        'workers': 2,
    }

    StandaloneApplication(app, options).run()
