#!/usr/bin/env python3
'Sensor Management'
### IMPORTS ###
import logging
import yaml

from string import Template

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Sensor:
    'Sensor class'
    def __init__(self, project, name , provider, uuid, size):
        self.logger = logging.getLogger(type(self).__name__)
        yaml_filename = "./manifests/sensor.template.yaml"

        with open(yaml_filename, mode='r', encoding='UTF-8') as file:
            contents = file.read()
            template = Template(contents)

        values = {
            'project': project,
            'size': size,
            'shortName': name,
            'provider': provider,
            'uuid': uuid
        }
        sensor_yaml=template.substitute(values)
        self._manifest=yaml.safe_load(sensor_yaml)

    @property
    def manifest(self):
        'Return YAML manifest'
        return self._manifest

    def save(self, project, name):
        'Save the Sensor to file'
        sensor_filename=f"{project}/{name}.sensor.yaml"
        sensor_file = open(sensor_filename, mode="w", encoding='UTF-8')
        yaml.dump(self.manifest, sensor_file)
        self.logger.info("Create Sensor: %s", sensor_filename)
