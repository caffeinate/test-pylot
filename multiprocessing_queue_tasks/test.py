'''
Created on 11 Jan 2016

@author: si
'''
import copy
import hashlib
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
            r[result[0]] = result[1]

        qe.join()
        self.got_correct_results(r)


if __name__ == "__main__":
    unittest.main()
