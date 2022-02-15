#!/usr/bin/env python3

### IMPORTS ###
import logging
import yaml

from string import Template

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Sensor:
    def __init__(self, name , provider, uuid, size):
        self.logger = logging.getLogger(type(self).__name__)
        yaml_filename = "./manifests/sensor.template.yaml"

        with open(yaml_filename, mode='r') as file:
            contents = file.read()
            template = Template(contents)

        values = {
            'size': size,
            'shortName': name,
            'provider': provider,
            'uuid': uuid
        }
        sensorYaml=template.substitute(values)
        self._manifest=yaml.safe_load(sensorYaml)

    @property
    def manifest(self):
        return self._manifest

    def save(self, project, name):
        sensorFilename=f"{project}/{name}.sensor.yaml"
        sensorFile = open(sensorFilename, "w")
        yaml.dump(self.manifest, sensorFile)
        self.logger.info("Create Sensor: %s", sensorFilename)
