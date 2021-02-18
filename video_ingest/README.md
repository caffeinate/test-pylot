# Demo Ingest

A quick demo of a batch ETL to create a single dataset from many small json files.


Run the tests it locally-

```shell
$ pipenv shell
$ pipenv install
$ python -m unittest video_ingest/test/test_*.py
```

## Setup

* Copy an existing config or look at BaseConfig class.
* Ensure the `destination_path` from config directory exists
* Ensure output subdirectories (`mkdir availability referential`) exist in the `destination_path` directory

Run it-

```shell
$ export PYTHONPATH=`pwd`
$ python video_ingest/acquire_pids/bootstrap_build.py deployment_environment
... split task across three workers
... just a demo so they are running sequentially
$ python video_ingest/acquire_pids/pids_worker.py deployment_environment --worker-ident 1:3
$ python video_ingest/acquire_pids/pids_worker.py deployment_environment --worker-ident 2:3
$ python video_ingest/acquire_pids/pids_worker.py deployment_environment --worker-ident 3:3
```
Where `deployment_environment` is the suffix for your config file's name.


