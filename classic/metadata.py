#!/usr/bin/env python3

### IMPORTS ###
import logging


from .exceptions import ManifestEmptyException, ManifestMissingValueException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Metadata:
    def __init__(self, manifest_dict = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not manifest_dict:
            raise ManifestEmptyException()

        self.logger.debug("Manifest Metadata: %s", manifest_dict)

        self._name = None
        if 'name' in manifest_dict:
            self.name = manifest_dict['name']
            self.logger.info("Manifest Metadata name: %s", manifest_dict['name'])

        self._project = None
        if 'project' in manifest_dict:
            self.project = manifest_dict['project']

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._name = value

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._project = value
