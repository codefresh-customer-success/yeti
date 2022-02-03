#!/usr/bin/env python3

### IMPORTS ###
import logging
import yaml

from string import Template

### GLOBALS ###

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
        self._manifest=yaml.safe_load(workflowTemplateYaml)

    @property
    def manifest(self):
        return self._manifest

    def save(self, project, name):
        workflowTemplateFilename=f"{project}/{name}.workflowTemplate.yaml"
        workflowTemplateFile = open(workflowTemplateFilename, "w")
        yaml.dump(self.manifest, workflowTemplateFile)
        self.logger.info("Create WorkflowTemplate: %s", workflowTemplateFilename)
