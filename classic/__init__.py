#!/usr/bin/env python3

### IMPORTS ###
import yaml
import logging

from .metadata import Metadata
from .exceptions import ManifestMissingValueException
from .exceptions import InvalidYamlAsPipeline


### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Classic:
    """Class related to Codefresh Classic operations and data"""

    def __init__(self,filename='pipeline.yaml'):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.info("Getting pipeline YAML in %s", filename)

        with open(filename, "r") as stream:
            try:
                self._manifest=yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.logger.error(exc)
                raise InvalidYamlAsPipeline(filename)
        if 'metadata' in self._manifest:
            self.metadata = Metadata(self._manifest['metadata'])
        else:
            self.logger.error("Pipeline Manifest missing 'metadata'")
            raise ManifestMissingValueException("Pipeline Manifest missing 'metadata'")
