#!/usr/bin/env python3

#
# Classic Triggers
#

### IMPORTS ###
import logging
#import string

from .exceptions import StepTypeNotSupported
from .exceptions import VariableNotSupportedInField
from .exceptions import  ShellTypeNotSupported


### GLOBALS ###

### FUNCTIONS ###


### CLASSES ###
class Step:
    def __init__(self, name, stype):

        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Creating New Step: %s", name)

        self.name = name
        self.type = stype

    #
    # Setters and getters
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
        self._type = value
