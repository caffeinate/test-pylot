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

## Run it

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


## Architecural Overview

Create a manifest file to hold the names of all source files. With this file plus code signatures (e.g. git commitishes) builds are deterministic and can be repeated. The `bootstrap_build.py` module creates this manifest file.

The ingest task is split across workers. The `Run it` example above uses three. These workers would run in parallel.

[Aye-aye](https://github.com/Aye-Aye-Dev/AyeAye) is used for the ETL. It makes it easy to have many versions of the source and destination datasets which are made available to the model at runtime. 

Aye-aye doesn't currently support GCS so the demo uses a local filesystem. GCSFuse could be used.

The output is a set of NDJSON files that could be loaded into Bigquery where a materialised join would create a table of all pids referential documents with a corresponding availability document.

The objective of the extract part of the ETL process is to create a simplified schema to make data discovery easy.
