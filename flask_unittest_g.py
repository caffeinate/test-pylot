'''
Created on 18 Nov 2015

@author: si
'''
from flask import Flask, g, current_app
import unittest

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def on_before_request(app):
    def before_request():
        msg = "before request? %s" % hasattr(g, "some_variable")
        current_app.logger.info(msg)
    return before_request

def on_after_request(app):
    def after_request(response):
        msg = "after request? %s" % hasattr(g, "some_variable")
        current_app.logger.info(msg)
        return response
    return after_request

def index():
    if hasattr(g, "some_variable"):
        return "Already defined"

    g.some_variable = "xyz"
    return "hello world!"

def create_app():
    app = Flask(__name__)
    app.before_request(on_before_request(app))
    app.after_request(on_after_request(app))
    app.add_url_rule('/', view_func=index)
    return app

class Test(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.test_client = self.app.test_client()

    def test_two_requests(self):
        #with self.app.app_context():
        rv = self.test_client.get('/')
        assert "hello world!" in rv.data
        rv = self.test_client.get('/')
        assert "hello world!" in rv.data

if __name__ == '__main__':
    #app = create_app()
    #app.run(debug=True, use_reloader=False, port=5060)
    unittest.main()