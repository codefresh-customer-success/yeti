#!/usr/bin/env python3

### IMPORTS ###
import logging
from string import Template
import yaml


### GLOBALS ###
def str_presenter(dumper, data):
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

### FUNCTIONS ###

### CLASSES ###
class WorkflowTemplate:
    '''Implementation fo the Workflow Tewmplate'''
    def __init__(self, name):
        self.logger = logging.getLogger(type(self).__name__)
        yaml_filename = "./manifests/workflowTemplate.template.yaml"

        with open(yaml_filename, mode='r', encoding='UTF-8') as file:
            contents = file.read()
            template = Template(contents)

        values = {
            'shortName': name
        }
        workflow_template_yaml=template.substitute(values)
        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter) # to use with safe_dum
        self._manifest=yaml.safe_load(workflow_template_yaml)

    @property
    def manifest(self):
        '''Return the YAML manifest'''
        return self._manifest

    def save(self, project, name):
        '''Save the workflow template as a file <project>/<name>.workflowtemplate.yaml'''
        workflow_template_filename=f"{project}/{name}.workflowTemplate.yaml"
        workflow_template_file = open(workflow_template_filename, "w", encoding='UTF-8')
        yaml.dump(self.manifest, workflow_template_file)
        self.logger.info("Create WorkflowTemplate: %s", workflow_template_filename)
