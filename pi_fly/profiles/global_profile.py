"""
Created on 22 Apr 2018

@author: si
"""


class BaseProfile(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HTTP_PORT = 8080
    ACTIONALS = []  # list of dictionaries.
    # See :function:`actional.actional_management.build_actional_processes`
    SESSION_PASSWORD = None  # must be set to a string if `valid_session` views are used

    # For gunicorn to use TLS set this to dictionary with keys "certfile" and "keyfile" each
    # having a value which is an absolute path to a .pem file.
    TLS_OPTIONS = None
