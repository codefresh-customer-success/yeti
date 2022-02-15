#!/usr/bin/env python3

### IMPORTS ###
import logging
import yaml

from string import Template

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
    def __init__(self, name):
        self.logger = logging.getLogger(type(self).__name__)
        yaml_filename = "./manifests/workflowTemplate.template.yaml"

        with open(yaml_filename, mode='r') as file:
            contents = file.read()
            template = Template(contents)

        values = {
            'shortName': name
        }
        workflowTemplateYaml=template.substitute(values)
        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter) # to use with safe_dum
        self._manifest=yaml.safe_load(workflowTemplateYaml)

    @property
    def manifest(self):
        return self._manifest

    def save(self, project, name):
        workflowTemplateFilename=f"{project}/{name}.workflowTemplate.yaml"
        workflowTemplateFile = open(workflowTemplateFilename, "w")
        yaml.dump(self.manifest, workflowTemplateFile)
        self.logger.info("Create WorkflowTemplate: %s", workflowTemplateFilename)
