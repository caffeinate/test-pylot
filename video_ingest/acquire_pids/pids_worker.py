from collections import defaultdict

import ayeaye

# TODO push partial substitution into ayaye.connect_resolve


class PartialSubstitute(dict):
    def __missing__(self, key):
        return '{' + key + '}'


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
            build_id (str) unique serial number/name for build
        """
        self.max_records_per_output_file = 10000
        self.worker_id = kwargs.pop('worker_id')
        self.workers_total = kwargs.pop('workers_total')
        self.build_id = kwargs.pop('build_id')
        super().__init__(*args, **kwargs)

    def build(self):

        stats = defaultdict(int)

        output_file_counter = 0
        records_current_file = defaultdict(int)  # demo multiple ndjson files per file type
        connector = {'availability': None,
                     'referential': None,
                     }
        self.log("Writing to output")
        for source_file in self.manifest.data.source_files:

            stats['total'] += 1

            if not self.file_in_scope(source_file):
                # this worker doesn't process this file
                continue

            if source_file.endswith('availability.json'):
                file_type = 'availability'
                document_extract = self.availability_extract(source_file)

            elif source_file.endswith('referential.json'):
                file_type = 'referential'
                document_extract = self.referential_extract(source_file)
            else:
                self.log(f'Unknown file type for {source_file}', "ERROR")
                continue

            if connector[file_type] is None:
                # write connector to ndjson files
                p = PartialSubstitute(file_number=output_file_counter,
                                      build_id=self.build_id,
                                      file_type=file_type,
                                      worker_id=self.worker_id
                                      )
                resolved_engine_url = self.simple_output_template.format_map(p)
                connector[file_type] = self.simple_output.add_engine_url(resolved_engine_url)
                output_file_counter += 1
                self.log(f"Writing to {connector[file_type].engine_url}")

            connector.add(document_extract)
            records_current_file[file_type] += 1

            if records_current_file[file_type] > self.max_records_per_output_file:
                connector[file_type] = None
                records_current_file[file_type] = 0

            stats['processed'] += 1

        self.log(f"Worker ID {self.worker_id} processed {stats['processed']} of {stats['total']}")
        self.log("Complete")

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

    def availability_extract(self, source_file):
        """
        Args:
            source_file (str) file path
        Returns:
            (dict) of useful fields
        """
        d = {}
        return d

    def referential_extract(self, source_file):
        """
        Args:
            source_file (str) file path
        Returns:
            (dict) of useful fields
        """
        # source file should be loaded by ayeaye
        d = {}
        return d


if __name__ == '__main__':
    from video_ingest.run_locally import local_context, config_context

    worker_id, workers_total = config_context['worker_ident'].split(':', 1)

    with local_context:
        m = PidsWorker(worker_id=worker_id,
                       workers_total=workers_total,
                       build_id=config_context['build_id']
                       )
        m.go()
