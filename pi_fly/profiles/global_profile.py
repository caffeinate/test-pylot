'''
Created on 22 Apr 2018

@author: si
'''


class BaseProfile(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HTTP_PORT = 8080
    ACTIONALS = []
    SESSION_PASSWORD = None  # must be set to a string if `valid_session` views are used
