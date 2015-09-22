#FlaskGunicorn

A python based daemon with worker threads with a built in webserver based on [Flask](http://flask.pocoo.org/) and [Gunicorn](http://gunicorn.org/).

This doesn't work for me....

Sharing variables with Flask requires dangerous assumptions on multiprocess + threads and Gunicorn must be in main thread because of signal handling. This is all more complex then the problem I'm trying to solve.

Next idea is [FlaskDaemon](../FlaskDaemon)
