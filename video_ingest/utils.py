'''
Created on 18 Feb 2021

@author: si
'''
import importlib
import os
import sys

manifest_prefix = 'manifest_'


def load_config(deployment_name):
    """
    Args:
        deployment_name (str) Name of deployment environment. Must be a file in in settings directory
                    with name config_<settings>.py

    Returns:
        obj subclass of :class:`config.base.BaseConfig`
    """
    config_modules_base = 'video_ingest.config'
    deployment_name = deployment_name
    config_module_path = f'{config_modules_base}.config_{deployment_name}'

    mod = importlib.import_module(config_module_path)
    config_cls = getattr(mod, 'Config')
    config = config_cls()
    return config


def parse_cli():
    """
    Really simple for demo.
    Deployment name is from single command line argument.
    Returns:
        (dict) with keys ['deployment_name', 'worker-ident']
    """
    # DEMO - use a proper library to do this
    if len(sys.argv) > 4 or len(sys.argv) < 2:
        calling_module = os.path.split(sys.argv[0])[1]
        msg = (f"usage: python {calling_module} <deployment> [--worker-ident X:Y]\n"
               "  where <deployment> in config file name as ./config/config_<deployment>.py\n"
               "  worker-ident is X (this worker) Y total workers\n"
               )
        sys.stderr.write(msg)
        sys.exit(-1)

    worker_ident = None

    deployment_name = sys.argv[1]
    if len(sys.argv) > 2:  # optional, not correctly parsed if id is missing
        assert sys.argv[2] == '--worker-ident'
        worker_ident = sys.argv[3]

    r = {'deployment_name': deployment_name,
         'worker_ident': worker_ident
         }
    return r
