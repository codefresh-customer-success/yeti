#!/usr/bin/env python3

### IMPORTS ###
import yaml
import logging

from .exceptions import ManifestMissingValueException
from .exceptions import InvalidYamlAsPipeline
from .exceptions import ParallelModeNotSupported

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
                pipeYaml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.logger.error(exc)
                raise InvalidYamlAsPipeline(filename)

        # Be sure we are loading a pipeline
        if not pipeYaml['kind'] == "pipeline":
            self.logger.critical("File should have a pipeline 'kind'")
            raise InvalidYamlAsPipeline(filename)


        self._yaml = pipeYaml
        self._project=pipeYaml['metadata']['project']
        self._shortName=pipeYaml['metadata']['shortName']
        self._fullName=pipeYaml['metadata']['name']
        # spec info
        self._triggers=pipeYaml['spec']['triggers']

        # No parallel mode for now
        if "mode" in pipeYaml['spec']:
            self._mode=pipeYaml['spec']['mode']
        else:
            self._mode="serial"
        if self._mode == "parallel":
            self.logger.critical("Parallel mode not supported")
            raise ParallelModeNotSupported(self._fullName)

    def print(self):
        print(f"v1.project:{self._project}")
        print(f"v1.name:{self._shortName}")
        #print(f"v1.yaml:{self._yaml}")
    @property
    def yaml(self):
        return self._yaml

    @property
    def project(self):
        return self._project

    @property
    def name(self):
        return self._shortName

    @property
    def fullName(self):
        return self._fullName

    @property
    def triggers(self):
        return self._triggers
