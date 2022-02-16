#!/usr/bin/env python3

### IMPORTS ###
import yaml
import logging
import utils
import re

from .exceptions import ManifestMissingValueException
from .exceptions import InvalidYamlAsPipeline
from .exceptions import ParallelModeNotSupported
#from .freestyle  import Freestyle
from .plugins    import Plugins
from .plugins    import Parameter

from .step       import Step

from .variable import Variable

#from ..utils import safeName

### GLOBALS ###

### FUNCTIONS ###
def grabFieldValue(block, field, defaultValue):
    value=defaultValue
    if field in block:
        value=block[field]
    return value

def parseRepo(str):
    if str.startswith("http"):
        list=str.split('/')
        repo=list[len(list)-1]
        repo=repo.replace(".git", "")
        owner=list[len(lits)-2]
    else:
        (owner, repo)=str.split('/')
    return (owner, repo)

def replaceParameterVariableByStepOutput(value, output):
    if '$' in value:
        # replace value of variable in working by output of named step
        regexp = r"\$\{{1,2}([^}]+)\}{1,2}"

        #
        # TODO:
        #  - add check to confirm this macthes a step name
        subst="{{ tasks.\\1.outputs.parameters.%s }}" %(output)
        # logging.debug("replaceParameterVariableByStepOutput - subst: %s", subst)
        value=re.sub(regexp, subst,value,0)
    return value

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
        self._project=utils.safeName(pipeYaml['metadata']['project'])
        self._shortName=utils.safeName(pipeYaml['metadata']['shortName'])
        self._fullName=pipeYaml['metadata']['name']

        self._secretVolumes=[]
        # variables
        self._variables=[]
        self.addVariable(Variable("CF_REPO_OWNER", "", "system", 0, "{{.Input.body.repository.owner.name}}"))
        self.addVariable(Variable("CF_REPO_NAME", "", "system", 1, "{{.Input.body.repository.name}}"))
        self.addVariable(Variable("CF_BRANCH", "", "system", 2, "{{.Input.body.ref}}"))

        # spec info
        self._triggers=pipeYaml['spec']['triggers']
        self._steps=[]
        for s in pipeYaml['spec']['steps']:
            self.addStep(s, pipeYaml['spec']['steps'][s])


        # No parallel mode for now
        self._mode="serial"
        if "mode" in pipeYaml['spec']:
            self._mode=pipeYaml['spec']['mode']

        if self._mode == "parallel":
            self.logger.critical("Parallel mode not supported")
            raise ParallelModeNotSupported(self._fullName)

    def createStep(self, name, block):
        stepType=grabFieldValue(block, "type", "freestyle")
        shell=grabFieldValue(block, "shell", "sh")
        cwd=grabFieldValue(block, "working_directory", "/codefresh/volume")
        cwd=replaceParameterVariableByStepOutput(cwd, "WORKING_DIR")

        if stepType == 'freestyle':
            commands=""
            if 'commands' in block:
                logging.debug("COMMAND: %s", block['commands'])
                str=''
                for line in block['commands']:
                    str += f"{line}\n"
                str += "\n"     # adding empty line to force | output
                commands=str

            image=replaceParameterVariableByStepOutput(block['image'], "IMAGE")
            #self.logger.debug("Freestyle step cwd: %s", cwd)

            #self.logger.debug("Freestyle step cwd after: %s", cwd)

            return Plugins(name, "freestyle", "0.0.1",
                [
                    Parameter('image',       self.replaceVariable(image)),
                    Parameter("working_directory", self.replaceVariable(cwd)),
                    Parameter("shell",       self.replaceVariable(shell)),
                    Parameter("commands",    commands)
                ])
        elif stepType == 'git-clone':
            (repoOwner, repoName) = parseRepo(block['repo'])
            return Plugins(name, "git-clone", "0.0.1",
                [
                    Parameter('CF_REPO_OWNER', self.replaceVariable(repoOwner)),
                    Parameter("CF_REPO_NAME", self.replaceVariable(repoName)),
                    Parameter("CF_BRANCH",    self.replaceVariable(block['revision']))
                ])
        elif stepType == 'build':
            tag=grabFieldValue(block, "tag", '${CF_BRANCH}')
            dockerfile=grabFieldValue(block, "dockerfile", "Dockerfile")
            registry=grabFieldValue(block, "registry", "docker-config")
            self.addSecretVolume(registry);
            return Plugins(name, "build", "0.0.1",
                [
                    Parameter('image_name', self.replaceVariable(block['image_name'])),
                    Parameter("tag", self.replaceVariable(block['tag'])),
                    Parameter("dockerfile", self.replaceVariable(dockerfile)),
                    Parameter("working_directory", self.replaceVariable(cwd)),
                    Parameter("docker-config", registry)
                ])
        else:
            raise StepTypeNotSupported(stepType)

    def replaceVariable(self, parameter):
        if not parameter:
            return parameter
        if not '$' in parameter:
            return parameter
        regexp = r"\$\{{1,2}([^}]+)\}{1,2}"
        subst="\\1"
        for v in self.variables:
            strippedParameter=re.sub(regexp, subst,parameter,0)
            if strippedParameter == v.name:
                return "{{ inputs.parameters.%s }}" % (strippedParameter)

    def addStep(self, name, block):
        self._steps.append(self.createStep(name, block))

    def addVariable(self, var):
        self._variables.append(var)

    def addSecretVolume(self, vol):
        self._secretVolumes.append(vol)

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

    @property
    def secretVolumes(self):
        return self._secretVolumes
