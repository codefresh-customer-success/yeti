#!/usr/bin/env python3

### IMPORTS ###
import logging
import uuid
import os

from .eventsource import EventSource

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Csdp:
    """Class related to Codefresh Classic operations and data"""
    def __init__(self, v1 = None):
        self.logger = logging.getLogger(type(self).__name__)
        uuidStr=str(uuid.uuid1())

        self.project = v1.project
        self.name = v1.name
        self.eventSource = EventSource(v1.name, "lrochette", "CF-tests", "github", uuidStr)


    def save(self):
        os.makedirs(self.project, exist_ok=True)
        self.eventSource.save(self.project, self.name)


    @property
    def eventSource(self):
        return self._eventSource

    @eventSource.setter
    def eventSource(self, value):
        if not value.manifest['kind'] == "EventSource":
            self.logger.error("This is not an event source")
            raise TypeError
        self._eventSource=value

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._project = value

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
