#!/usr/bin/env python3

#
# Classic Triggers
#

### IMPORTS ###
import logging

from .step import Step

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Parameter:
    def __init__(self, pName, pValue):
        self.logger = logging.getLogger(type(self).__name__)
        self.name=pName
        self.value=pValue

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._name = value
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, val):
        self._value = val

class Plugins(Step):
    def __init__(self, name, pluginName, version, parameters):
        self.logger = logging.getLogger(type(self).__name__)

        super().__init__(name, "plugins")
        self.pluginName=pluginName
        self.pluginVersion=version
        self.parameters=parameters

    @property
    def pluginName(self):
        return self._pluginName
    @pluginName.setter
    def pluginName(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._pluginName = value

    @property
    def pluginVersion(self):
        return self._pluginVersion
    @pluginVersion.setter
    def pluginVersion(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._pluginVersion = value

    @property
    def parameters(self):
        return self._parameters
    @parameters.setter
    def parameters(self, value):
        self._parameters = value
