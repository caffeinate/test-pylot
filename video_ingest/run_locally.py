'''
Created on 18 Feb 2021

@author: si
'''
import glob
import os

import ayeaye

from video_ingest.utils import load_config, parse_cli, manifest_prefix

# Demo only for local execution
# make variables available to ETL at runtime
cli_params = parse_cli()
config = load_config(deployment_name=cli_params['deployment_name'])

full_path = os.path.abspath(config.destination_path)
search_path = os.path.join(full_path, f'{manifest_prefix}*')
all_manifests = [r for r in glob.glob(search_path)]
all_manifests.sort()
# this is a demo! more deterministic choice need
manifest_file = all_manifests[-1]
build_id = manifest_file[-15:-5]

config_context = {'manifest_file_path': manifest_file,
                  'worker_ident': cli_params['worker_ident'],
                  'destination_path': config.destination_path,
                  'source_path': config.source_path,
                  'build_id': build_id,
                  }
local_context = ayeaye.connector_resolver.context(**config_context)
