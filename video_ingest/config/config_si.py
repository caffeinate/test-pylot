import os
from video_ingest.config.base import BaseConfig

DATA_LIBRARY_PATH = '/Users/si/Documents/Scratch/ingest_demo/'


class Config(BaseConfig):
    #     source_path = os.path.join(DATA_LIBRARY_PATH, 'source')
    source_path = '/Users/si/Documents/LocalCode/test-pylot/video_ingest/test/data'
    destination_path = os.path.join(DATA_LIBRARY_PATH, 'destination')
