#FlaskGunicornSqlAlchemy

The objective is to produce a RESTful API and measure the throughput compared with straight SqlAlchemy access.

Each simulated user connection will make a combination of read and write requests.

##Scenarios

### Locking

1. Transaction
1. Optimistic

### Engine
1. InnoDB
1. MyISAM

### HTTP
1. 1.0
1. 1.1 with keep alive

### Concurrency
1. No. of Server threads
1. No. of Server processes
1. No. of client threads
1. No. of requests per client
1. Read/write ratio of client requests

## Install
apt-get install libevent-dev python-all-dev python-mysqldb
pip install gunicorn gevent flask-cors flask_sqlalchemy

```Python
from flask_app import db, create_app
app = create_app('config.Config')
with app.app_context():
  db.create_all()
```

```Shell
si@xenial:~/Desktop/FlaskGunicornSqlAlchemy$ python main.py 
[2017-03-31 12:29:41 +0000] [31048] [INFO] Starting gunicorn 19.7.1
[2017-03-31 12:29:41 +0000] [31048] [INFO] Listening at: http://127.0.0.1:8080 (31048)
[2017-03-31 12:29:41 +0000] [31048] [INFO] Using worker: gevent
[2017-03-31 12:29:41 +0000] [31055] [INFO] Booting worker with pid: 31055
[2017-03-31 12:29:41 +0000] [31056] [INFO] Booting worker with pid: 31056
[2017-03-31 12:29:41 +0000] [31057] [INFO] Booting worker with pid: 31057
```

