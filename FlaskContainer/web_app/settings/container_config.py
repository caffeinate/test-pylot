import os

from web_app.settings.global_config import BaseConfig

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config(BaseConfig):
    pass
