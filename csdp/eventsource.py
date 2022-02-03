#!/usr/bin/env python3

### IMPORTS ###
import logging
import yaml

from string import Template

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class EventSource:
    def __init__(self, name, owner, repoName, provider, uuid):
        self.logger = logging.getLogger(type(self).__name__)
        yaml_filename = "./manifests/eventsource.template.yaml"

        with open(yaml_filename, mode='r') as file:
            contents = file.read()
            template = Template(contents)

        values = {
            'shortName': name,
            'owner': owner,
            'repoName': repoName,
            'provider': provider,
            'uuid': uuid
        }
        eventSourceYaml=template.substitute(values)
        self._manifest=yaml.safe_load(eventSourceYaml)

    @property
    def manifest(self):
        return self._manifest

    def save(self, project, name):
        esFilename=f"{project}/{name}.event-source.yaml"
        esFile = open(esFilename, "w")
        yaml.dump(self.manifest, esFile)
        self.logger.info("Create Event source: %s", esFilename)