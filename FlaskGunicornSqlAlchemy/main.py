from __future__ import unicode_literals

import multiprocessing
import gunicorn.app.base

from gunicorn.six import iteritems

from flask_app import create_app

def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1
    #return 2


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
        'workers': 5,
        'threads': 10,
        'keepalive': 1,
        'worker_class': 'sync',
        'log-level': 'debug',
    }
    app = create_app('config.Config')
    StandaloneApplication(app, options).run()

