'''
Created on 19 Jun 2015

@author: si
'''
import json
import unittest

from flask_app import create_app, db
from config import TestConfig as Config

SHOW_LOG_MESSAGES = False

if not SHOW_LOG_MESSAGES:
    # when local log is switched off, also hide logs from app below CRITICAL
    import logging
    logging.disable(logging.ERROR)


class FooTest(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.app = create_app(self.config)
        self.test_client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        self.config.drop_db()

    def log(self, msg):
        if SHOW_LOG_MESSAGES:
            print msg

    def test_empty_root(self):
        rv = self.test_client.get('/')
        assert 'Hello' in rv.data

    def test_add_foo(self):
 
        testUrl = '/foo/'

        with self.app.app_context():
            #create_permissions_universe(db)
            raw = { 'title' : 'hellofoo' }
            d = json.dumps(raw)
            rv = self.test_client.post(testUrl,
                                       data=d,
                                       content_type='application/json')
            response = json.loads(rv.data)

            assert response['success'] == True

if __name__ == '__main__':
    unittest.main()
