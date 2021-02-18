from datetime import datetime
import glob
import json
import os

from video_ingest.utils import load_config, parse_cli, manifest_prefix


class BootstrapBuild:
    """
    Create a manifest file which contains all the information needed for a build to be repeatable.

    For example, store all the files that will be processed by workers.
    """

    def __init__(self, config, manifest_prefix):
        """
        Args:
            config (obj) with attribs:
                        source_path
                        destination_path
            see config.base.BaseConfig

            manifest_prefix (str) start of name of manifest files
        """
        self.config = config
        self.manifest_prefix = manifest_prefix

    def create_manifest(self):

        existing_manifests = self.existing_manifests()
        for counter in range(1000):

            if counter >= 999:
                raise ValueError("Can't find an available manifest name")

            build_ref = "{}_{}".format(datetime.utcnow().strftime('%Y%m%d'), counter)
            filename = f"{self.manifest_prefix}{build_ref}.json"
            if filename not in existing_manifests:
                break

        manifest_path = os.path.join(self.config.destination_path, filename)
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest_content(), f, indent=4)

    def existing_manifests(self):
        """
        Return:
            (list of str) filenames, not paths of existing manifest files.
        """
        full_path = os.path.abspath(self.config.destination_path)
        path_len = len(full_path)
        search_path = os.path.join(full_path, '*')

        files = []
        for r in glob.glob(search_path):
            files.append(r[path_len + 1:])

        return files

    def manifest_content(self):
        """
        The manifest should contain anything need to reproduce the build at a later date. For
        example, data version numbers, code versions e.g. git commitishes.

        Returns:
            (dict) that will serialise into JSON
        """
        r = {'created': datetime.utcnow().isoformat(),
             }

        # TODO
        return r


if __name__ == '__main__':

    deployment_environment = parse_cli()
    config = load_config(deployment_name=deployment_environment)

    bootstrap = BootstrapBuild(config=config, manifest_prefix=manifest_prefix)
    bootstrap.create_manifest()
