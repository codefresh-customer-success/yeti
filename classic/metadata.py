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

        self.logger.info("Manifest Metadata: %s", manifest_dict)
        self.logger.info("Manifest Metadata name: %s", manifest_dict['name'])

        self._name = None
        if 'name' in manifest_dict:
            self.name = manifest_dict['name']

        self._project = None
        if 'project' in manifest_dict:
            self.project = manifest_dict['project']

    @property
    def name(self):
        return self._name

    @property
    def project(self):
        return self._project
