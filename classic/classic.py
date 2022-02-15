#!/usr/bin/env python3

### IMPORTS ###
import yaml
import logging
import utils

from .exceptions import ManifestMissingValueException
from .exceptions import InvalidYamlAsPipeline
from .exceptions import ParallelModeNotSupported
from .step import Step
from .variable import Variable

#from ..utils import safeName

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

        self.logger.debug(pipeYaml)

        self._yaml = pipeYaml
        self._project=utils.safeName(pipeYaml['metadata']['project'])
        self._shortName=utils.safeName(pipeYaml['metadata']['shortName'])
        self._fullName=pipeYaml['metadata']['name']
        # spec info
        self._triggers=pipeYaml['spec']['triggers']
        self._steps=[]
        for s in pipeYaml['spec']['steps']:
            self.addStep(s, pipeYaml['spec']['steps'][s])

        # variables
        self._variables=[]
        self.addVariable(Variable("CF_REPO_OWNER", "", "system", 0, "{{.Input.body.repository.owner.name}}"))
        self.addVariable(Variable("CF_REPO_NAME", "", "system", 1, "{{.Input.body.repository.name}}"))
        self.addVariable(Variable("CF_BRANCH", "", "system", 2, "{{.Input.body.ref}}"))

        # No parallel mode for now
        self._mode="serial"
        if "mode" in pipeYaml['spec']:
            self._mode=pipeYaml['spec']['mode']

        if self._mode == "parallel":
            self.logger.critical("Parallel mode not supported")
            raise ParallelModeNotSupported(self._fullName)


    def addStep(self, name, block):
        self._steps.append(Step(name, block))

    def addVariable(self, var):
        self._variables.append(var)

    def print(self):
        print(f"v1.project:{self._project}")
        print(f"v1.name:{self._shortName}")
        #print(f"v1.yaml:{self._yaml}")
    @property
    def manifest(self):
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
    def mode(self):
        return self._mode
    @property
    def triggers(self):
        return self._triggers

    @property
    def steps(self):
        return self._steps

    @property
    def variables(self):
        return self._variables
