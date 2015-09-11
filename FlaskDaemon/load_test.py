'''
Created on 11 Sep 2015

@author: si
'''
import json
import random
import time
from threading import Thread
# import urllib
import urllib2
from Queue import Queue

import logging
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:5000/"

class LoadTest(object):
    """
    Create a single process with one thread per test user.
    """

    def __init__(self, test_users_count, requests_per_user):
        """
        @param test_users_count: int
        @param requests_per_user: int 
        """

        self.thread_table = []
        self.test_users_count = test_users_count
        self.requests_per_user = requests_per_user
        
        self.stats = {  'return_codes' : {},
                        'requests_made' : 0,
                        'total_seconds_waiting' : 0.0
                    }
        self.stats_q = Queue(0)

    def go(self):

        start_time = time.time()

        msg = "%s test users with %s requests each..." % \
                                (self.test_users_count, self.requests_per_user)
        self.logger(msg)
        for i in range(self.test_users_count):
            p = TestUser(i, self.requests_per_user, self.stats_q)
            p.start()
            self.thread_table.append(p)

        end_time = time.time()
        self.logger("time taken to create threads : %s"  % (end_time-start_time,))

        start_time = time.time()
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

    def __init__(self, user_id, requests_count, stats_queue):
        super(TestUser, self).__init__()
        self.remaining_request = requests_count
        self.base_url = API_URL
        self.stats_queue = stats_queue
        self.user_id = user_id

    def logger(self, msg):
        logger.info(msg)
        #print msg

    def run(self):
        """
        @return: dictionary of stats to be collected by main process
        """
        stats = {   'return_codes' : {},
                    'requests_made': self.remaining_request,
                    'total_seconds_waiting' : 0.0, # waiting for requests
                 }
        while self.remaining_request > 0:

            # sleep for average of half a second
            time.sleep(random.random())

            start_time = time.time()

            # for POST
            #raw = {}
            #d = json.dumps(raw)
            #h = {'Content-type': 'application/json'}
            #req = urllib2.Request(self.base_url, data=d, headers=h)

            # for GET
            req = urllib2.Request(self.base_url)
            f = urllib2.urlopen(req)
            end_time = time.time()

            d = end_time-start_time
            stats['total_seconds_waiting'] += d

            http_status = f.getcode()
            if http_status not in stats['return_codes']:
                stats['return_codes'][http_status] = 0
            stats['return_codes'][http_status] += 1

            self.remaining_request -= 1

        self.logger("Thread %s finished: %s" % (self.user_id, stats))
        self.stats_queue.put(stats, False)



if __name__ == '__main__':
    l = LoadTest(10,30)
    l.go()   
