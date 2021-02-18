import os
from video_ingest.config.base import BaseConfig

DATA_LIBRARY_PATH = '/Users/si/Documents/Scratch/ingest_demo/'


class Config(BaseConfig):
    source_path = os.path.join(DATA_LIBRARY_PATH, 'source')
    destination_path = os.path.join(DATA_LIBRARY_PATH, 'destination')
