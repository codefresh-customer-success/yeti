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
from .step import grab_field_value
from .step import replace_parameter_variable_by_step_output

### GLOBALS ###

### FUNCTIONS ###


def parse_repo_field(string):
    '''Parse the repo field to extract owner/name if it's a URL'''
    if string.startswith("http"):
        chunks=string.split('/')
        repo=chunks[len(chunks)-1]
        repo=repo.replace(".git", "")
        owner=chunks[len(chunks)-2]
    else:
        (owner, repo)=string.split('/')
    return (owner, repo)



### CLASSES ###
class Classic:
    """Class related to Codefresh Classic operations and data"""
    def __init__(self,filename='pipeline.yaml'):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.info("Getting pipeline YAML in %s", filename)

        with open(filename, "r", encoding='UTF-8') as stream:
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

        self._variables=[]
        self.add_variable(Variable("CF_REPO_OWNER", "", "system",
            0, "{{.Input.body.repository.owner.name}}"))
        self.add_variable(Variable("CF_REPO_NAME", "", "system",
            1, "{{.Input.body.repository.name}}"))
        self.add_variable(Variable("CF_BRANCH", "", "system", 2, "{{.Input.body.ref}}"))
        variable_counter=3
        for var in pipeline_yaml['spec']['variables']:
            self.add_variable(Variable(var['key'], var['value'], "pipeline", variable_counter, ""))
            variable_counter = +1

        # spec info
        self._triggers=pipeline_yaml['spec']['triggers']
        self._steps=[]
        for step in pipeline_yaml['spec']['steps']:
            self.add_step(step, pipeline_yaml['spec']['steps'][step])

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
        cwd=grab_field_value(block, "working_directory", "/codefresh/volume")
        cwd=replace_parameter_variable_by_step_output(cwd, "WORKING_DIR")

        if step_type == 'freestyle':
            shell=grab_field_value(block, "shell", "sh")
            commands=""
            if 'commands' in block:
                logging.debug("COMMAND: %s", block['commands'])
                string=''
                for line in block['commands']:
                    string += f"{line}\n"
                string += "\n"     # adding empty line to force | output
                commands=string
 
            image=replace_parameter_variable_by_step_output(block['image'], "IMAGE")
            #self.logger.debug("Freestyle step cwd: %s", cwd)
            #self.logger.debug("Freestyle step cwd after: %s", cwd)

            return Plugins(name,  "freestyle", "0.0.1", block,
                [
                    Parameter('image',       self.replace_variable(image)),
                    Parameter("working_directory", self.replace_variable(cwd)),
                    Parameter("shell",       self.replace_variable(shell)),
                    Parameter("commands",    commands)
                ])
        elif step_type == 'git-clone':
            (repo_owner, repo_name) = parse_repo_field(block['repo'])
            return Plugins(name, "git-clone", "0.0.1", block,
                [
                    Parameter('CF_REPO_OWNER', self.replace_variable(repo_owner)),
                    Parameter("CF_REPO_NAME", self.replace_variable(repo_name)),
                    Parameter("CF_BRANCH",    self.replace_variable(block['revision']))
                ])
        elif step_type == 'build':
            tag=grab_field_value(block, "tag", '${CF_BRANCH}')
            dockerfile=grab_field_value(block, "dockerfile", "Dockerfile")
            registry=grab_field_value(block, "registry", "docker-config")
            self.add_secret_volume(registry);
            return Plugins(name, "build", "0.0.1", block,
                [
                    Parameter('image_name', self.replace_variable(block['image_name'])),
                    Parameter("tag", self.replace_variable(tag)),
                    Parameter("dockerfile", self.replace_variable(dockerfile)),
                    Parameter("working_directory", self.replace_variable(cwd)),
                    Parameter("docker-config", registry)
                ])
        elif '/' in step_type:
            self.logger.critical("Typed step not supported %s",step_type)
            raise StepTypeNotSupported("Typed step")
        else:
            raise StepTypeNotSupported(step_type)

    def replace_variable(self, parameter):
        '''Try to replace a variable ${{}} by a matching input parameter'''
        if not parameter:
            return parameter
        if not '$' in parameter:
            return parameter
        regexp = r"\$\{{1,2}([^}]+)\}{1,2}"
        subst="\\1"
        for var in self.variables:
            stripped_parameter=re.sub(regexp, subst,parameter,0)
            if stripped_parameter == var.name:
                return "{{ inputs.parameters.%s }}" % (stripped_parameter)

    def add_step(self, name, block):
        '''Add the step YAML block the Classic object'''
        self._steps.append(self.create_step(name, block))

    def add_variable(self, var):
        '''Add a Variable to the Classic Object'''
        self._variables.append(var)

    def add_secret_volume(self, vol):
        '''Add a secret Volume (for docker secret for example) to the Classic object'''
        self._secret_volumes.append(vol)

    def print(self):
        '''Method to print the Classic object'''
        print(f"v1.project:{self._project}")
        print(f"v1.name:{self._short_name}")
        #print(f"v1.yaml:{self._yaml}")
    @property
    def manifest(self):
        '''Return the manifest Yaml'''
        return self._yaml

    @property
    def project(self):
        '''Return the project name'''
        return self._project

    @property
    def name(self):
        '''return the pipleine short name - no project'''
        return self._short_name

    @property
    def full_name(self):
        '''Return the full name of the pipeline'''
        return self._full_name

    @property
    def mode(self):
        '''Return the pipeline mode aka parallel'''
        return self._mode
    @property
    def triggers(self):
        '''Return the list of triggers'''
        return self._triggers

    @property
    def steps(self):
        '''Return the list of steps'''
        return self._steps

    @property
    def variables(self):
        '''Return the list of variables'''
        return self._variables

    @property
    def secretVolumes(self):
        '''Return the list of secret volumes'''
        return self._secret_volumes
