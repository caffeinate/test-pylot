'''
from https://github.com/caffeinate/test-pylot/tree/master/multiprocessing_queue_tasks
Created on 2 Nov 2015

@author: si
'''
from collections import namedtuple
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
        self.results_queue = Queue() # is given tuples
                                    # ( worker_id,
                                    #   task_item (converted to string),
                                    #   task_result
                                    # )
        self.map_func = map_func
        self.number_procs = number_procs
        self.finished = Value('i', 0) # indicates no further input will be given
        self.processing_started = Value('i', 0)
        self.n_added_to_queue = 0
        self.n_results_from_queue = 0
        self.print_log = False

        def queue_execute_worker(tasks_q, results_q, func, worker_id):

            while True:
                try:
                    input_item = tasks_q.get(block=False)
                    # do some stuff
                    result = func(input_item)
                    # stick the output somewhere
                    results_q.put((worker_id, input_item, result))
                    #tasks_q.task_done()
                except Empty:
                    if self.finished.value == 1 \
                        and self.processing_started.value == 1:
                        # possible for processing_started to be set between
                        # tasks_q.get() and exception
                        time.sleep(0.1)
                        if tasks_q.qsize() == 0:
                            break
                    # maybe replace sleep with a Condition
                    self.log("worker %s sleeping..." % worker_id)
                    time.sleep(0.25)
                    continue

            self.log("worker %s ending" % worker_id)

        self.worker = queue_execute_worker

    def log(self, msg):
        if self.print_log:
            print msg

    def add_worker(self, func):
        """
        Add a single worker. Must be called before .run()

        @param func: function or callable which takes single item as supplied
                    to add_task_item(..)
        """
        worker_id = len(self.process_table)
        proc_args = (self.task_queue, self.results_queue, func, worker_id)
        p = Process(target=self.worker, args=proc_args)
        self.process_table.append(p)

    def add_task_item(self, x):
        self.n_added_to_queue += 1
        self.task_queue.put(x)
    
    def get_result(self):
        """
        generator yielding each item in self.results_queue as namedtuple
        with fields-

        * process_id
        * result_value
        * input

        """
        ResultItem = namedtuple('ResultItem', ['worker_id',
                                               'result_value',
                                               'input'
                                               ]
                                )
        while True:
            try:
                r = self.results_queue.get(block=False)
                self.n_results_from_queue += 1
                yield ResultItem(worker_id=r[0],
                                 result_value=r[2],
                                 input=r[1]
                                 )
            except Empty:
                if self.finished.value == 1\
                    and self.n_added_to_queue == self.n_results_from_queue:
                    break
                self.log("results sleeping")
                # maybe replace sleep with a Condition
                time.sleep(0.25)
                continue
        return

    def finished_adding_items(self):
        """
        Signal that all items have been added and process should end when
        all items have been processed. 
        """
        self.log("signal to finish recieved")
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

        this method isn't thread safe
        """
        proc_table_size = len(self.process_table)
        for proc_index in range(self.number_procs):
            proc_args = (self.task_queue, self.results_queue, self.map_func,
                         proc_index+proc_table_size)
            p = Process(target=self.worker, args=proc_args)
            self.process_table.append(p)

        for p in self.process_table:
            p.start()

        self.processing_started.value = 1
