#!/usr/bin/env python3

### IMPORTS ###
import logging
import yaml
import os

from string import Template

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Ingress:
    def __init__(self, project):
        self.logger = logging.getLogger(type(self).__name__)

        #
        # If ingress file exist, load it
        #
        filename=f"{project}/{project}.ingress.yaml"
        if os.path.isfile(filename):
            with open(filename, mode='r') as file:
                try:
                    ingressYaml = yaml.safe_load(file)
                except yaml.YAMLError as exc:
                    self.logger.error(exc)
                    raise InvalidYamlAsIngress(filename)

        #
        # If not, create from template
        else:
            self.logger.info("Creating new Ingress")
            yaml_filename = "./manifests/ingress.template.yaml"
            with open(yaml_filename, mode='r') as file:
                contents = file.read()
                template = Template(contents)

                values = {
                    'project': project
                }
                ingressYaml=template.substitute(values)

        self._manifest = yaml.safe_load(ingressYaml)
        self.logger.debug("Ingress code: %s", self._manifest)

    @property
    def manifest(self):
        return self._manifest

    def save(self, project):
        ingressFilename=f"{project}/{project}.ingress.yaml"
        ingressFile = open(ingressFilename, "w")
        yaml.dump(self.manifest, ingressFile)
        self.logger.info("Create Ingress: %s", ingressFilename)
