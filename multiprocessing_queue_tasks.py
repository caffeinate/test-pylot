'''
Created on 2 Nov 2015

@author: si
'''
import hashlib
from multiprocessing import Queue, Process, Value
from Queue import Empty
import time

class QueueExecute(object):
    """
    Pool of processes (not threads) for dealing with a continuous stream of
    tasks rather than the usual set of tasks which are known at beginning.

    Results are also in a queue so can be removed at any time.
    
    JoinableQueue not much help with this scenario.
    
    Example usage-
    >>> from multiprocessing_queue_tasks import QueueExecute, crypto_challenge
    >>> qe = QueueExecute(6, crypto_challenge)       
    >>> qe.run()
    >>> for a in "0123456789abcdef":
    ...   qe.add_task_item(a)
    ... 
    >>> qe.finished_adding_items()
    >>> for result in qe.get_result():
    ...   print "got result", result
    ... 
    got result ('0', 126)
    got result ('3', 763)
    got result ('4', 1622)
    got result ('5', 2796)
    got result ('2', 5744)
    got result ('6', 6268)
    got result ('8', 1916)
    got result ('7', 8559)
    got result ('a', 27)
    got result ('1', 11962)
    got result ('b', 4457)
    got result ('d', 2456)
    got result ('c', 5934)
    got result ('f', 5174)
    got result ('e', 7473)
    got result ('9', 12804)
    >>> qe.join()
    
    """
    def __init__(self, number_procs=0, map_func=None):
        """
        @param number_procs: int
        @param map_func: function which takes one argument

        @see add_worker(..)
        """
        self.process_table = []
        self.task_queue = Queue()
        self.results_queue = Queue() # is given tuples (task_item, task_result)
        self.map_func = map_func
        self.number_procs = number_procs
        self.finished = Value('i', 0) # indicates no further input will be given
        self.n_added_to_queue = 0
        self.n_results_from_queue = 0
        self.print_log = False

        def queue_execute_worker(tasks_q, results_q, func):

            while True:
                try:
                    for c in tasks_q.get(block=False):
                        # do some stuff
                        result = func(c)
                        # stick the output somewhere
                        results_q.put((str(c), result))
                        #tasks_q.task_done()
                except Empty:
                    if self.finished.value == 1:
                        break
                    # maybe replace sleep with a Condition
                    self.log("sleeping")
                    time.sleep(0.5)
                    continue
            self.log("worker ending")

        self.worker = queue_execute_worker

    def log(self, msg):
        if self.print_log:
            print msg

    def add_worker(self, func):
        """
        @param func: function or callable which takes single item as supplied
                    to add_task_item(..)
        """
        proc_args = (self.task_queue, self.results_queue, func)
        p = Process(target=self.worker, args=proc_args)
        self.process_table.append(p)

    def add_task_item(self, x):
        self.n_added_to_queue += 1
        self.task_queue.put(x)
    
    def get_result(self):
        """
        generator
        """
        while True:
            try:
                r = self.results_queue.get(block=False)
                self.n_results_from_queue += 1
                yield r
            except Empty:
                if self.finished.value == 1\
                    and self.n_added_to_queue == self.n_results_from_queue:
                    break
                self.log("sleeping")
                # maybe replace sleep with a Condition
                time.sleep(0.5)
                continue
        return

    def finished_adding_items(self):
        self.finished.value = 1
    
    def join(self):
        """
        wait for processes to finish, does not join queues
        """
        self.log("waiting on processes")
        for p in self.process_table:
            p.join()
     
        self.log("all processes have terminated")
    
    def run(self):
        """
        start processes executing
        """
        proc_args = (self.task_queue, self.results_queue, self.map_func)
        for proc_index in range(self.number_procs):
            p = Process(target=self.worker, args=proc_args)
            self.process_table.append(p)

        for p in self.process_table:
            p.start()


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

if __name__ == '__main__':

    n_procs = 6
    qe = QueueExecute(n_procs, crypto_challenge)
    qe.print_log = True
    qe.run()    

    for a in "0123456789abcdef":
        qe.add_task_item(a)

    #time.sleep(3.)    
    qe.finished_adding_items()

    for result in qe.get_result():
        print "got result", result

    qe.join()

    print "process completed"
