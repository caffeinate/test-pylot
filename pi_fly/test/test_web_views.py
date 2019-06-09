'''
Created on 27 Mar 2019

@author: si
'''
from datetime import datetime
from multiprocessing import Process

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pi_fly.actional.actional_management import build_actional_processes, governor_run_forever
from pi_fly.model import Sensor, Base
from pi_fly.scoreboard import ScoreBoard
from pi_fly.web_view import create_app

from .test_base import BaseTest

class TestWebViews(BaseTest):

    def setUp(self):
        super().setUp()

        self.scoreboard = ScoreBoard()
        self.app = create_app(self.config, self.scoreboard)
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

        # used by tests that spin up more of the system, e.g. actionals
        self.proc_table = []

    def tearDown(self):
        super().tearDown()
        self.request_context.pop()

        if self.proc_table:
            self.shutdown_procs()

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

    def run_actionals(self):
        """
        run actionals from config and governor to manage them. Store
        details to allow :method:`shutdown_procs` on self.
        """
        actional_details = build_actional_processes(self.config, self.scoreboard)
        ac_names = []
        self.proc_table = []
        for ac_name, ac_parts in actional_details.items():
            # can't pickle a process so just put the comms part on
            self.scoreboard.update_value(ac_name, {'comms': ac_parts['comms']})
            ac_names.append(ac_name)
            self.proc_table.append(ac_parts['process'])
            ac_parts['process'].start()

        p = Process(target=governor_run_forever, args=(self.scoreboard, ac_names, None))
        self.proc_table.append(p)
        p.start()

    def shutdown_procs(self):
        for p in self.proc_table:
            p.terminate()

        for p in self.proc_table:
            if p.is_alive():
                p.join()

        self.proc_table = []

    def test_run_command(self):
        """
        actionals should make a available a list of commands and it should be possible to
        send a command to an actional's comms pipe via the scoreboard.
        """
        self.run_actionals()

        rv = self.test_client.get('/run_command/')
        self.assertEqual(200, rv.status_code)
        # Command from :class:`actional.dummy.DummyActional`
        self.assertIn(b'Log &#34;hello command ABC&#34;', rv.data)

        # next POST it
        rv = self.test_client.post('/run_command/',
                                   data={'actional_name': 'fake_actional_0',
                                         'command': 'ABC',
                                        }
                                   )
        self.assertEqual(200, rv.status_code)
        # Command from :class:`actional.dummy.DummyActional`
        self.assertIn(b'Running....fake_actional_0 .. ABC', rv.data)
