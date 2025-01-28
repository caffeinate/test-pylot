"""
Run a Flask app using gunicorn in a container.

inspired by-
https://github.com/Aye-Aye-Dev/Fossa
"""

import gunicorn.app.base

from web_app.app import create_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """
    Run a WSGI web-app using gunicorn.
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run_flask_app(deployment_config):
    """
    Use gunicorn to run Flask app.

    @param deployment_config: (str or class or anything accepted by Flask's `app.config.from_object`)
        Used to choose the settings file. i.e. 'prod' uses .....settings.prod_config.Config
    """
    app = create_app(deployment_config)

    options = {
        "bind": "%s:%s" % ("0.0.0.0", app.config["HTTP_PORT"]),
        "workers": 4,
        "syslog": True,
        "timeout": 80,
    }
    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    config_package = f"web_app.settings.container_config.Config"
    run_flask_app(config_package)
