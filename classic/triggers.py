#!/usr/bin/env python3

### IMPORTS ###
import logging

from .exceptions import OnlySupportGitTriggerException
### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Triggers:
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)


#
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
        if not value == "git"
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
