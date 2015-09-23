'''
Created on 23 Sep 2015

@author: si
'''
from sqlalchemy import Column, Integer, Numeric, String, Table, Date, ForeignKey
# from sqlalchemy.dialects.mysql import INTEGER, DOUBLE
from sqlalchemy.orm import relationship, backref

from sqlalchemy import orm, event
from sqlalchemy.orm.exc import UnmappedClassError

from flask_app import db

class Foo(db.Model):
    __tablename__ = 'foo'

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    proc_id = Column(Integer)
    thread_name = Column(String(20))

    def __repr__(self):
        return '<Foo %r>' % (self.id)

    @property
    def serialize(self):
        return {'title' : self.title,
                'proc_id' : self.proc_id,
                'thread_name' : self.thread_name,
                }
