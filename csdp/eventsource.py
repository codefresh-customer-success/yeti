#!/usr/bin/env python3

### IMPORTS ###
import logging
import yaml

from string import Template

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class EventSource:
    def __init__(self, name, provider, uuid):
        self.logger = logging.getLogger(type(self).__name__)
        yaml_filename = "./manifests/eventsource.template.yaml"

        with open(yaml_filename, mode='r') as file:
            contents = file.read()
            template = Template(contents)

        self.logger.debug("Init EventSource - uuid: %s", uuid)
        values = {
            'shortName': name,
            'provider': provider,
            'uuid': uuid
        }
        eventSourceYaml=template.substitute(values)
        self._manifest=yaml.safe_load(eventSourceYaml)

    @property
    def manifest(self):
        return self._manifest

    @manifest.setter
    def manifest(self, value):
        self._manifest=value

    def save(self, project, name):
        esFilename=f"{project}/{name}.event-source.yaml"
        esFile = open(esFilename, "w")
        yaml.dump(self.manifest, esFile)
        self.logger.info("Create Event source: %s", esFilename)
