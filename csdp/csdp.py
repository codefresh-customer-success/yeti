#!/usr/bin/env python3

### IMPORTS ###
import logging
import uuid
import os

from .eventsource import EventSource
from .sensor import Sensor
from .workflow_template import WorkflowTemplate
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
        self.sensor = Sensor(v1.name, "github", uuidStr)
        self.workflowTemplate = WorkflowTemplate(v1.name)

    def save(self):
        os.makedirs(self.project, exist_ok=True)
        self.eventSource.save(self.project, self.name)
        self.sensor.save(self.project, self.name)
        self.workflowTemplate.save(self.project, self.name)

### Setters and getters
    @property
    def workflowTemplate(self):
        return self._workflowTemplate

    @workflowTemplate.setter
    def workflowTemplate(self, value):
        if not value.manifest['kind'] == "WorkflowTemplate":
            self.logger.error("This is not a workflowTemplate")
            raise TypeError
        self._workflowTemplate=value

    @property
    def sensor(self):
        return self._sensor

    @sensor.setter
    def sensor(self, value):
        if not value.manifest['kind'] == "Sensor":
            self.logger.error("This is not a sensor")
            raise TypeError
        self._sensor=value

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
