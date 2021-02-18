import unittest

from video_ingest.config.config_test import Config
from video_ingest.acquire_pids.bootstrap_build import BootstrapBuild
from video_ingest.utils import manifest_prefix


class TestBootstrap(unittest.TestCase):

    def test_create_single_manifest(self):

        c = Config()
        b = BootstrapBuild(config=c, manifest_prefix=manifest_prefix)

        msg = "Should have empty set of manifests before bootstrap"
        self.assertEqual([], b.existing_manifests(), msg)

        b.create_manifest()

        manifests = b.existing_manifests()
        self.assertEqual(1, len(manifests), "Should have a single manifest file")
