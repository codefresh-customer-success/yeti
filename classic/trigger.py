#!/usr/bin/env python3

#
# Classic Triggers
#

### IMPORTS ###
import logging

from .exceptions import OnlySupportGitTriggerException
from .exceptions import OnlyOneEventSupportbyTrigger

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Trigger:
    def __init__(self, trig = None):
        self.logger = logging.getLogger(type(self).__name__)

        if not trig:
            raise EmptyObjectException("trigger")

        self._name = None
        if 'name' in trig:
            self.name = trig['name']
            self.logger.info("Trigger name: %s", trig['name'])

        self.type = trig['type']
        self.repo = trig['repo']
        self.provider = trig['provider']
        self.events = trig['events']

    def print(self):
        print(f"Trigger.name: {self.name}")
        print(f"Trigger.repo: {self.repo}")
        print(f"Trigger.provider: {self.provider}")
        print(f"Trigger.type: {self.type}")
        printf(f"Trigger.events: {self.events}")


# setters and getters
#
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
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value == "git":
            raise OnlySupportGitTriggerException
        if len(value) < 3:
            raise ValueError
        self._type= value

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._repo = value

    @property
    def events(self):
        return self._events
    @events.setter
    def events(self, value):
        if len(value) > 1:
            raise OnlyOneEventSupportbyTrigger
        event=value[0]
        if event.startswith("push"):
            event="push"
        self._events = event

    @property
    def provider(self):
        return self._provider

    @type.setter
    def provider(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value == "github":
            raise OnlySupportGithubProvider
        if len(value) < 3:
            raise ValueError
        self._type = value
