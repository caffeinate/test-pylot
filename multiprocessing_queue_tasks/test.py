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

class CallBasedCryptoChallenge(object):

    def __init__(self, task_id):
        self.task_id = task_id

    def __call__(self, *args):
        return crypto_challenge(*args)

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
        qe = QueueExecute(2, crypto_challenge)
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
        self.assertEqual(','.join(worker_ids_l), '0,1,2')

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

    def test_callable(self):
        """
        Workers use a callable object instead of a function.
        """
        qe = QueueExecute()
        for a in "0123456789abcdef":
            qe.add_task_item(a)

        # finish called before any processing has been done
        qe.finished_adding_items()

        for i in range(2):
            qe.add_worker(CallBasedCryptoChallenge(i))

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
        self.assertEqual(','.join(worker_ids_l), '0,1')

    def test_duplicate_items(self):
        """
        one item on task_queue should be one item off the results_queue
        """

        def no_work(i):
            return i

        qe = QueueExecute(6, no_work)
        #qe.print_log = True
        qe.run()

        input_size = 200
        for a in range(input_size):
            qe.add_task_item(a)

        qe.finished_adding_items()

        r = {}
        for result in qe.get_result():
            #print "got result", result
            r[result.input] = result.result_value

        qe.join()
        self.assertEqual(len(r.keys()), input_size)

    def test_separate_generator(self):
        """
        add some items to input queue and then "one in one out" of
        QueueExecute
        """

        def no_work(i):
            return i

        def generator():
            i=0
            while True:
                yield i
                i += 1


        parallel_processes = 5
        records_generator = generator()

        queue_processor = QueueExecute()
        for task_id in range(parallel_processes):

            sub_processor = no_work
            queue_processor.add_worker(sub_processor)

        queue_processor.run()


        initial_buffer_size = parallel_processes * 5
        r_count = 0
        for _record in records_generator:
            #print "pre sending:%s" % _record
            queue_processor.add_task_item(_record)
            r_count += 1
            if r_count >= initial_buffer_size:
                break

        result_generator = queue_processor.get_result()
        # one in one out from here
        r = []
        for _record in records_generator:

            #print "post sending:%s" % _record

            # careful - a StopIteration here would be a fail because there
            # are def. results pending
            result = next(result_generator)
            r.append(result.result_value)

            if _record > 100:
                break

            # add record to queue
            queue_processor.add_task_item(_record)

        # end of input stream signalled to sub-processes
        queue_processor.finished_adding_items()

        # wait for remaining results
        for result in result_generator:
            r.append(result.result_value)

        # wait for processes to finish
        queue_processor.join()

        self.assertEqual(101, len(r))

if __name__ == "__main__":
    unittest.main()
