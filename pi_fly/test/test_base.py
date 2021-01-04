'''
Created on 31 Jan 2019

@author: si
'''
import unittest
import warnings

from pi_fly.profiles.test_profile import Profile

import logging
logging.disable(logging.ERROR)


class BaseTest(unittest.TestCase):
    def setUp(self):

        self.profile = Profile()
        #self.app = create_app(self.profile)
        self.show_log_messages = True

        warning_msg = ('Dialect sqlite\+pysqlite does \*not\* support Decimal'
                       ' objects natively')
        warnings.filterwarnings('ignore', warning_msg)

        #self.test_client = self.app.test_client()

        #self.request_context = self.app.test_request_context()
        # self.request_context.push()

    def tearDown(self):
        self.profile.drop_db()
        warnings.resetwarnings()
        # self.request_context.pop()

    def log(self, msg):
        if self.show_log_messages:
            print(msg)
