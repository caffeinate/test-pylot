import ayeaye


class PidsWorker(ayeaye.Model):
    """
    Extract useful fields from pids availability and referential files into multiple NDJSON files.

    The output files are laid out for HIVE partitioning and can be joined in BigQuery.

    Multiple PidsWorkers work on the transform task in parallel.
    """
    manifest = ayeaye.Connect(engine_url="json://{manifest_file_path}")

    # The output consists of multiple NDJSON files in HIVE partitioned layout
    output_template = ('ndjson://{destination_path}/{file_type}/build_id={build_id}/'
                       '{worker_id}_{file_number}.ndjson'
                       )
    availability_output = ayeaye.Connect(engine_url=[], access=ayeaye.AccessMode.WRITE)

    referential_output = ayeaye.Connect(engine_url=[], access=ayeaye.AccessMode.WRITE)

    def __init__(self, *args, **kwargs):
        """
        Args:
            worker_id (int) id of the current worker
            workers_total (int) number of workers processing this task
        """
        self.worker_id = kwargs.pop('worker_id')
        self.workers_total = kwargs.pop('workers_total')
        super().__init__(*args, **kwargs)

    def build(self):
        pass

    def file_in_scope(self, file_name):
        """
        Args:
            file_name (str)
        Returns
            bool indicating if the current worker (self) (with worker_id) should process
            the file.
        """
        # DEMO - hash uses a salt, not suitable as different machines would have different results
        # just using it for demo as it produces an int
        h = abs(hash(file_name))
        target_worker = h % self.workers_total
        return target_worker == self.worker_id
