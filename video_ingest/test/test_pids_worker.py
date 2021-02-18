import unittest

from video_ingest.acquire_pids.pids_worker import PidsWorker


class TestPidsWorker(unittest.TestCase):

    def test_scoped_file(self):
        """
        Only one pids_worker should process each input file.

        So filter the input files into one list per worker; join these back up and they
        should match the input files without anything missing or duplicated.
        """
        input_files = ['a', 'b', 'c', 'd']

        workers_count = 3
        worker_files = []  #  list of lists
        for worker_id in range(workers_count):
            w = PidsWorker(worker_id=worker_id, workers_total=workers_count)
            # this is the list of files that this worker has accepted to process
            this_workers_files = list(filter(w.file_in_scope, input_files))
            worker_files.append(this_workers_files)

        msg = "Output set of files should equal number of workers"
        self.assertEqual(workers_count, len(worker_files), msg)

        all_processed_files = []
        for file_set in worker_files:
            all_processed_files += file_set

        all_processed_files.sort()
        input_files.sort()
        self.assertEqual(input_files, all_processed_files)
