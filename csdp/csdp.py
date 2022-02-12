#!/usr/bin/env python3

### IMPORTS ###
import logging
import uuid
import os

from .eventsource import EventSource
from .sensor import Sensor
from .workflow_template import WorkflowTemplate
#from ..classic import Trigger

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Csdp:
    """Class related to Codefresh Classic operations and data"""
    def __init__(self, v1 = None):
        self.logger = logging.getLogger(type(self).__name__)
        self.uuid=str(uuid.uuid1())
        self.project = v1.project
        self.name = v1.name
        self.eventSource = EventSource(name=v1.name, provider="github", uuid=self.uuid)
        self.sensor = Sensor(v1.name, "github", self.uuid)
        self.workflowTemplate = WorkflowTemplate(v1.name)

    def save(self):
        os.makedirs(self.project, exist_ok=True)
        self.eventSource.save(self.project, self.name)
        self.sensor.save(self.project, self.name)
        self.workflowTemplate.save(self.project, self.name)

    def convertTrigger(self, trig):
        #
        # Add to EventSource:

        # spec
        #   github:
        #     github-d8a7c62d-2f2a-40c0-a0d4-139c957fd762:
        #       events:
        #         - push
        #       repositories:
        #         - owner: lrochette
        #           names:
        #             - express-microservice

        (owner,repoName) = trig.repo.split('/')
        self.logger.debug("Convert Trigger %s", self.name)
        self.logger.debug("  owner %s", owner)
        self.logger.debug("  repo name %s", repoName)
        block = {
            "events": trig.events ,
            "repositories": [{
                "owner": owner,
                "names": [repoName]
            }]
        }
        self.eventSource.manifest['spec'][trig.provider][trig.provider + "-" + self.uuid]=block

    def convertStep(self, step):
        pass
        
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

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value
