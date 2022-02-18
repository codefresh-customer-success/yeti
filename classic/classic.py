#!/usr/bin/env python3

### IMPORTS ###
import logging
import re
import yaml
import utils


#from .exceptions import ManifestMissingValueException
from .exceptions import InvalidYamlAsPipeline
from .exceptions import ParallelModeNotSupported
from .exceptions import StepTypeNotSupported
from .plugins    import Plugins
from .plugins    import Parameter

from .variable import Variable


### GLOBALS ###

### FUNCTIONS ###
def grab_field_value(block, field, default_value):
    '''Return the field value from the yaml block if it exists 
       or return the default valye'''
    value=default_value
    if field in block:
        value=block[field]
    return value

def parse_repo_field(string):
    '''Parse the repo field to extract owner/name if it's a URL'''
    if str.startswith("http"):
        chunks=string.split('/')
        repo=chunks[len(chunks)-1]
        repo=repo.replace(".git", "")
        owner=chunks[len(chunks)-2]
    else:
        (owner, repo)=string.split('/')
    return (owner, repo)

def replace_parameter_variable_by_step_output(value, output):
    '''replace ${{}} reference from a field to the correct output from a previous step
       - a clone step, will return a WORKING_DIR to be use as a working_dir
       - build step will return an IMAGE
    '''
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

        with open(filename, encoding='UTF-8', "r") as stream:
            try:
                pipeline_yaml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.logger.error(exc)
                raise InvalidYamlAsPipeline(filename) from exc

        # Be sure we are loading a pipeline
        if not pipeline_yaml['kind'] == "pipeline":
            self.logger.critical("File should have a pipeline 'kind'")
            raise InvalidYamlAsPipeline(filename)

        self._yaml = pipeline_yaml
        self._project=utils.safe_name(pipeline_yaml['metadata']['project'])
        self._short_name=utils.safe_name(pipeline_yaml['metadata']['shortName'])
        self._full_name=pipeline_yaml['metadata']['name']

        self._secret_volumes=[]
        # variables
        self._variables=[]
        self.add_variable(Variable("CF_REPO_OWNER", "", "system", 0, "{{.Input.body.repository.owner.name}}"))
        self.add_variable(Variable("CF_REPO_NAME", "", "system", 1, "{{.Input.body.repository.name}}"))
        self.add_variable(Variable("CF_BRANCH", "", "system", 2, "{{.Input.body.ref}}"))
        variable_counter=3
        for var in pipeline_yaml['spec']['variables']:

        # spec info
        self._triggers=pipeline_yaml['spec']['triggers']
        self._steps=[]
        for s in pipeline_yaml['spec']['steps']:
            self.addStep(s, pipeline_yaml['spec']['steps'][s])


        # No parallel mode for now
        self._mode="serial"
        if "mode" in pipeline_yaml['spec']:
            self._mode=pipeline_yaml['spec']['mode']

        if self._mode == "parallel":
            self.logger.critical("Parallel mode not supported")
            raise ParallelModeNotSupported(self._full_name)

    def create_step(self, name, block):
        '''Check the type of step to create the correct class object'''
        step_type=grab_field_value(block, "type", "freestyle")
        shell=grab_field_value(block, "shell", "sh")
        cwd=grab_field_value(block, "working_directory", "/codefresh/volume")
        cwd=replace_parameter_variable_by_step_output(cwd, "WORKING_DIR")

        if step_type == 'freestyle':
            commands=""
            if 'commands' in block:
                logging.debug("COMMAND: %s", block['commands'])
                str=''
                for line in block['commands']:
                    str += f"{line}\n"
                str += "\n"     # adding empty line to force | output
                commands=str

            image=replace_parameter_variable_by_step_output(block['image'], "IMAGE")
            #self.logger.debug("Freestyle step cwd: %s", cwd)

            #self.logger.debug("Freestyle step cwd after: %s", cwd)

            return Plugins(name, "freestyle", "0.0.1",
                [
                    Parameter('image',       self.replaceVariable(image)),
                    Parameter("working_directory", self.replaceVariable(cwd)),
                    Parameter("shell",       self.replaceVariable(shell)),
                    Parameter("commands",    commands)
                ])
        elif step_type == 'git-clone':
            (repoOwner, repoName) = parse_repo_field(block['repo'])
            return Plugins(name, "git-clone", "0.0.1",
                [
                    Parameter('CF_REPO_OWNER', self.replaceVariable(repoOwner)),
                    Parameter("CF_REPO_NAME", self.replaceVariable(repoName)),
                    Parameter("CF_BRANCH",    self.replaceVariable(block['revision']))
                ])
        elif step_type == 'build':
            tag=grab_field_value(block, "tag", '${CF_BRANCH}')
            dockerfile=grab_field_value(block, "dockerfile", "Dockerfile")
            registry=grab_field_value(block, "registry", "docker-config")
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
            raise StepTypeNotSupported(step_type)

    def replace_variable(self, parameter):
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

    def add_step(self, name, block):
        self._steps.append(self.create_step(name, block))

    def add_variable(self, var):
        self._variables.append(var)

    def add_secret_volume(self, vol):
        self._secret_volumes.append(vol)

    def print(self):
        print(f"v1.project:{self._project}")
        print(f"v1.name:{self._short_name}")
        #print(f"v1.yaml:{self._yaml}")
    @property
    def manifest(self):
        return self._yaml

    @property
    def project(self):
        return self._project

    @property
    def name(self):
        return self._short_name

    @property
    def fullName(self):
        return self._full_name
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
        return self._secret_volumes
