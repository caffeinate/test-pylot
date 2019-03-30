'''
Created on 27 Mar 2019

@author: si
'''
from datetime import datetime
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pi_fly.model import Sensor, Base
from pi_fly.scoreboard import ScoreBoard
from pi_fly.web_view import create_app

from .test_base import BaseTest

class TestWebViews(BaseTest):

    def setUp(self):
        super().setUp()

        self.app = create_app(self.config, ScoreBoard())
        self.test_client = self.app.test_client()

        # useful when using DB in memory
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        
        # database is normally created by the DatabaseStoragePollingLoop and web view
        # consumes from this db. But this unit test shouldn't be concerned with
        # DatabaseStoragePollingLoop so doing own create.
        engine = create_engine(self.config.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        self.db_session = DBSession()

    def tearDown(self):
        super().tearDown()
        self.request_context.pop()

    def test_empty_db(self):
        rv = self.test_client.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertIn(b'No sensor readings in DB', rv.data)

    def test_dashboard(self):
        """
        The last value from sensor table in db should be on the dashboard.
        """
        # sensor_id for water is currently hard coded into the dashboard's view
        reading = {'last_updated': datetime.utcnow(),
                   'sensor_id': '28-0015231007ee',
                   'value_type': 'temperature', 
                   'value_float': 123.4,
                   }
        r = Sensor(**reading)
        self.db_session.add(r)
        self.db_session.commit()

        rv = self.test_client.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertIn(b'123', rv.data, "Temperature should be rounded to nearest degree")

    def test_scoreboard(self):
        """
        Check the shared memory for holding sensor values can be accessed.
        """
        values_read = {'sensor_id': None,
                       'value_type': "time",
                       'value_float': 1553982125.797958
                       }
        self.app.sensor_scoreboard.update_value('fake_input', values_read)

        rv = self.test_client.get('/sensor_scoreboard/')
        self.assertEqual(200, rv.status_code)
        self.assertIn(b'1553982125.797958', rv.data, "Time of fake input sensor not found.")
