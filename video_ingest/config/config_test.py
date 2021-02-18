import os
import tempfile
import shutil

from .base import BaseConfig

TESTS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'test')


class Config(BaseConfig):

    def __init__(self):
        self._temp_working_directory = tempfile.mkdtemp()
        self.destination_path = os.path.join(self._temp_working_directory, 'destination')

        # example files
        self.source_path = os.path.join(TESTS_PATH, 'data')

        os.mkdir(self.destination_path)

    def __del__(self):
        if self._temp_working_directory and os.path.isdir(self._temp_working_directory):
            shutil.rmtree(self._temp_working_directory)
