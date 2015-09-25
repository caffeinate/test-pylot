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

```Python
from flask_app import db, create_app
app = create_app('config.Config')
with app.app_context():
  db.create_all()
```