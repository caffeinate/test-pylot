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
    Simple command line parser. Just one argument is needed - the deployment environment's name.

    Returns:
        (str) deployment name
    """
    if len(sys.argv) != 2:
        calling_module = os.path.split(sys.argv[0])[1]
        msg = (f"usage: python {calling_module} <deployment>\n"
               "  where <deployment> in config file name as ./config/config_<deployment>.py\n"
               )
        sys.stderr.write(msg)
        sys.exit(-1)

    deployment_environment = sys.argv[1]
    assert deployment_environment.isalnum(), "Dynamic module loading might not be safe"
    return deployment_environment
