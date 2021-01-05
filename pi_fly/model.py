'''
Created on 14 Apr 2018

@author: si
'''
from datetime import datetime

from sqlalchemy import Column, Integer, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, unique=True, primary_key=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    sensor_id = Column(Text, index=True)
    value_type = Column(Text)
    value_float = Column(Float)


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, unique=True, primary_key=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    start = Column(DateTime, index=True)
    end = Column(DateTime)
    source = Column(Text, index=True)
    label = Column(Text)
