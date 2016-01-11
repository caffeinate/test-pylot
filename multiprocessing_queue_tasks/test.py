'''
Created on 11 Jan 2016

@author: si
'''
import copy
import hashlib
import pickle
import unittest

from multiprocessing_queue_tasks import QueueExecute

def crypto_challenge(ch):
    """
    @param ch: ascii character found in an md5sum

    return an int which is the length of a string composed of 'ch'
    which has the md5sum starting with count number of 'ch'

    e.g.
    >>> crypto_challenge('a',3)
    27

    [si@buru ~]$ echo -n aaaaaaaaaaaaaaaaaaaaaaaaaaa | md5sum
    aaab9c59a88bf0bdfcb170546c5459d6  -
    [si@buru ~]$

    inspired by the bitcoin mining algorithm.
    """
    count = 3 # complexity, lower the number = quicker

    s = ""
    while(True):
        md5 = hashlib.md5(s).hexdigest()
        if md5[0:count] == str(ch) * count:
            return len(s)
        s += ch

def crypto_challenge_attrib_based(a):
    return crypto_challenge(a.item)

class AttribBased(object):
    """
    dot attrib access to variables in a way which might not serialise.
    """
    def __init__(self, data=None):
        if data:
            self.att = data
        else:
            self.att = {}

    def __repr__(self):
        d = ', '.join(["%s:%s" % (k,v) for k,v in self.att.iteritems()])
        return '<AttribBased %s>' % d

    def __setattr__(self, attr, val):
        if attr != 'att':
            self.att[attr] = val
        else:
            super(AttribBased, self).__setattr__(attr, val)

    def __getattr__(self, attr):
        if attr == 'att':
            return {}
        return self.att[attr]

    def __getstate__(self):
        return self.att

    def __setstate__(self, state):
        self.att = state

class Test(unittest.TestCase):

    def got_correct_results(self, results):
        """
        @param results: dictionary
        """
        r = copy.copy(results)
        # known correct results
        expected = [('0', 126),
                    ('3', 763),
                    ('4', 1622),
                    ('8', 1916),
                    ('5', 2796),
                    ('a', 27),
                    ('6', 6268),
                    ('b', 4457),
                    ('2', 5744),
                    ('d', 2456),
                    ('c', 5934),
                    ('e', 7473),
                    ('f', 5174),
                    ('7', 8559),
                    ('1', 11962),
                    ('9', 12804),
                    ]

        for input, expected_out in expected:
            self.assertEqual(expected_out, r[input])
            del r[input]

        self.assertTrue(len(r) == 0)

    def test_basic_usage(self):
        qe = QueueExecute(6, crypto_challenge)
        #qe.print_log = True
        qe.run()

        for a in "0123456789abcdef":
            qe.add_task_item(a)

        qe.finished_adding_items()

        r = {}
        for result in qe.get_result():
            #print "got result", result
            r[result.input] = result.result_value

        qe.join()
        self.got_correct_results(r)

    def test_extra_process(self):
        """
        After calling .run(), add another process.
        """
        qe = QueueExecute(3, crypto_challenge)
        for a in "0123456789abcdef":
            qe.add_task_item(a)

        # finish called before any processing has been done
        qe.finished_adding_items()

        # add another worker (must be done before .run())
        qe.add_worker(crypto_challenge)

        # start processing
        qe.run()

        r = {}
        worker_ids_seen = set()
        for result in qe.get_result():
            #print "got result", result
            r[result.input] = result.result_value
            worker_ids_seen.add(str(result.worker_id))

        qe.join()
        self.got_correct_results(r)

        # All worker processes should have done some work
        worker_ids_l = list(worker_ids_seen)
        worker_ids_l.sort()
        self.assertEqual(','.join(worker_ids_l), '0,1,2,3')

    def test_zero_items(self):
        """
        If no items are given to process, it shouldn't hang waiting.
        """
        qe = QueueExecute(3, crypto_challenge)
        #qe.print_log = True
        qe.finished_adding_items()
        qe.run()
        for result in qe.get_result():
            raise ValueError("Shouldn't get here")

        qe.join()
        # should get here OK

    def test_attrib_based(self):

        qe = QueueExecute(3, crypto_challenge_attrib_based)
        #qe.print_log = True
        for a in "0123456789abcdef":
            ab = AttribBased(data={'item':a})
            #ab_str = pickle.dumps(ab)
            qe.add_task_item(ab)

        qe.run()
        qe.finished_adding_items()

        r = {}
        for result in qe.get_result():
            r[result.input.item] = result.result_value

        qe.join()
        self.got_correct_results(r)

    def test_attrib_class(self):
        ab = AttribBased({'item':'xx'})
        p = pickle.dumps(ab)
        ab2 = pickle.loads(p)
        self.assertEqual('xx', ab2.item)

if __name__ == "__main__":
    unittest.main()
