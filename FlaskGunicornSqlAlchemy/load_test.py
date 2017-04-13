'''
Create a load of threads and test a web engine by making requests from each thread.

@author: si
'''
import json
import hashlib
import random
import requests
import time
from threading import Thread
import urllib2
import httplib, urllib
from Queue import Queue
import threading
import os

import logging
logger = logging.getLogger(__name__)


API_HOST = '127.0.0.1'
API_PORT = 8080
API_URL = "http://%s:%s/" % (API_HOST, API_PORT)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
from config import Config
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
#engine.pool._use_threadlocal = True

class Foo(Base):
    __tablename__ = 'foo'

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    proc_id = Column(Integer)
    thread_name = Column(String(20))


class LoadTest(object):
    """
    Create a single process with one thread per test user.
    """

    def __init__(self, test_users_count, requests_per_user, read_to_write_ratio):

        self.thread_table = []
        self.test_users_count = test_users_count
        self.requests_per_user = requests_per_user
        self.read_to_write_ratio = read_to_write_ratio
        
        self.stats = {  'return_codes' : {},
                        'requests_made' : 0,
                        'total_seconds_waiting' : 0.0,
                        'read_requests': 0,
                        'write_requests': 0,
                        'http_by_proc-thread': set(),
                    }
        self.stats_q = Queue(0)

    def go(self):

        start_time = time.time()

        msg = "%s test users with %s requests each..." % \
                                (self.test_users_count, self.requests_per_user)
        self.logger(msg)
        for i in range(self.test_users_count):
            p = TestUser(i, self.requests_per_user, self.read_to_write_ratio,
                         self.stats_q)
            p.start()
            self.thread_table.append(p)

        end_time = time.time()
        time_taken = str(end_time-start_time)
        self.logger("time taken to create threads : %s"  % time_taken)

        # wait for threads to complete
        while True:
            alive_count = len(self.thread_table)

            # could time.sleep(0.5) or just wait for all threads to finish
            for p in self.thread_table:
                if not p.is_alive():
                    alive_count -= 1
                else:
                    p.join()
            
            if alive_count == 0:
                break

            #print "alive:%s" % alive_count

        end_time = time.time()
        time_taken = end_time-start_time
        self.logger("finished. Time taken : %s"  % time_taken)


        while not self.stats_q.empty():
            user_stats = self.stats_q.get()
            for http_status, count in user_stats['return_codes'].iteritems():
                if http_status not in self.stats['return_codes']:
                    self.stats['return_codes'][http_status] = 0
                self.stats['return_codes'][http_status] += count
            self.stats['requests_made'] += user_stats['requests_made']
            self.stats['total_seconds_waiting'] += user_stats['total_seconds_waiting']
            self.stats['read_requests'] += user_stats['read_requests']
            self.stats['write_requests'] += user_stats['write_requests']
            self.stats['http_by_proc-thread'] = self.stats['http_by_proc-thread']\
                                                .union(user_stats['http_by_proc-thread'])

        print self.stats
        # time_taken is real time not CPU
        req_per_sec = float(self.stats['requests_made'])/time_taken
        print "Requests per second: %s" % req_per_sec

    def logger(self, msg):
        logger.info(msg)
        print msg



class TestUser(Thread):
    """
    Act like a user. Bit over simplified at the moment.
    """

    def __init__(self, user_id, requests_count, read_to_write_ratio, stats_queue):
        super(TestUser, self).__init__()
        self.remaining_request = requests_count
        self.base_url = API_URL
        self.stats_queue = stats_queue
        self.user_id = user_id
        self.read_to_write_ratio = read_to_write_ratio
        self.write_if_below = 1./read_to_write_ratio

    def logger(self, msg):
        logger.info(msg)
        #print msg

    def run(self):
        #return self.run_sqlalchemy_test()
        return self.run_api_test()

    def run_sqlalchemy_test(self):
        """
        @return: dictionary of stats to be collected by main process
        """
        stats = {   'return_codes' : {},
                    'requests_made': self.remaining_request,
                    'total_seconds_waiting' : 0.0, # waiting for requests
                 }
        
        Session = sessionmaker(bind=engine)
        session = Session()

        request_verb = "POST"
        #request_verb = "GET"

        stats['return_codes'][200] = 0
        stats['return_codes'][404] = 0

        while self.remaining_request > 0:

            # sleep for average of half a second
            #time.sleep(random.random())

            start_time = time.time()

            if request_verb == "GET":
                foo_id = int(random.random()*3700)
                try:
                    foo = session.query(Foo).filter_by(id=foo_id).one()
                    if len(foo.title) < 1:
                        print 'fail'
                    stats['return_codes'][200] += 1
                except NoResultFound:
                    stats['return_codes'][404] += 1

            else:
                r = {   'title' : hashlib.md5(str(random.random())).hexdigest()[0:6],
                        'proc_id' : str(os.getpid()),
                        'thread_name' : threading.current_thread().name,
                     }
                foo = Foo(**r)
                session.add(foo)
                session.commit()

            end_time = time.time()
            
            stats['total_seconds_waiting'] += end_time-start_time
            self.remaining_request -= 1

        self.logger("Thread %s finished: %s" % (self.user_id, stats))
        self.stats_queue.put(stats, False)

    def run_api_test(self):
        """
        @return: dictionary of stats to be collected by main process
        """
        stats = {   'return_codes' : {},
                    'requests_made': self.remaining_request,
                    'total_seconds_waiting' : 0.0, # waiting for requests
                    'read_requests': 0,
                    'write_requests': 0,
                    'http_by_proc-thread': set(),
                 }
        url = self.base_url+'foo/'
        
        #request_mode = "urllib2"
        #request_mode = "httplib"
        request_mode = "requests"

        if request_mode == "httplib":
            conn = httplib.HTTPConnection(API_HOST, API_PORT)
        
        if request_mode == "requests":
            conn = requests.session()
            conn.keep_alive = False

        while self.remaining_request > 0:

            if random.random() < self.write_if_below:
                request_verb = "POST"
                stats['write_requests'] += 1
            else:
                request_verb = "GET"
                stats['read_requests'] += 1

            # sleep for average of half a second
            #time.sleep(random.random())

            if request_verb == "GET":
                foo_id = int(random.random()*3700)
                url_get = 'foox/'+str(foo_id)+'/'
                url = self.base_url+url_get

            raw = { 'title' : hashlib.md5(str(random.random())).hexdigest()[0:6]
                 }
            d = json.dumps(raw)
            #params = urllib.urlencode(raw)
            h = {"Content-type": "application/json",
                 "Connection":" keep-alive"
                 }

            if request_mode == "urllib2":
                if request_verb == "GET":
                    req = urllib2.Request(url)
                else:
                    req = urllib2.Request(url, data=d, headers=h)
                start_time = time.time()
                f = urllib2.urlopen(req)
                end_time = time.time()
                http_status = f.getcode()

            elif request_mode == "httplib":
                start_time = time.time()
                if request_verb == "GET":
                    conn.request('GET', '/'+url_get)
                else:
                    conn.request('POST', '/foo/', d, h)
                response = conn.getresponse()
                if response.status == 200:
                    data = json.loads(response.read())
                    stats['http_by_proc-thread'].add(data['http_by_proc-thread'])
                end_time = time.time()
                http_status = response.status
                #print data

            elif request_mode == "requests":
                start_time = time.time()
                if request_verb == "GET":
                    r = conn.get(url)
                else:
                    h = {'Content-type': 'application/json'}
                    r = conn.post(url,
                               data=d,
                               headers=h
                               )

                if r.status_code == 200:
                    data = r.json()
                    stats['http_by_proc-thread'].add(data['http_by_proc-thread'])
                end_time = time.time()
                http_status = r.status_code


            stats['total_seconds_waiting'] += end_time-start_time
            
            if http_status not in stats['return_codes']:
                stats['return_codes'][http_status] = 0
            stats['return_codes'][http_status] += 1

            self.remaining_request -= 1

        if request_mode == "httplib":
            conn.close()

        self.logger("Thread %s finished: %s" % (self.user_id, stats))
        self.stats_queue.put(stats, False)


if __name__ == '__main__':
    test_users_count = 5
    requests_per_user = 50
    read_to_write_ratio = 90./10.
    l = LoadTest(test_users_count, requests_per_user, read_to_write_ratio)
    l.go()   
