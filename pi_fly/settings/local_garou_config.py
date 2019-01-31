'''
Created on 25 Jan 2019

@author: si
'''
from .global_config import BaseConfig

class Config(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/si/Desktop/sensors.db"
