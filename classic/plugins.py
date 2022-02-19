#!/usr/bin/env python3
'''
Plugin class to repesent typed-step nad freestyle
'''
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
    '''Parameter to a plugins'''
    def __init__(self, name, value):
        self.logger = logging.getLogger(type(self).__name__)
        self.name=name
        self.value=value

    @property
    def name(self):
        'Return the name of the parameter'
        return self._name
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._name = value
    @property
    def value(self):
        'Return the value of the parameter'
        return self._value
    @value.setter
    def value(self, val):
        self._value = val

class Plugins(Step):
    'Special step to call typed-step and freestyle'
    def __init__(self, name, plugin_name, version,  block, parameters):
        self.logger = logging.getLogger(type(self).__name__)

        super().__init__(name, "plugins", block)
        self.plugin_name=plugin_name
        self.plugin_version=version
        self.parameters=parameters

    @property
    def plugin_name(self):
        'Return the name of the plugin'
        return self._plugin_name
    @plugin_name.setter
    def plugin_name(self, value):
        if not isinstance(value, str):
            raise TypeError
        self._plugin_name = value

    @property
    def plugin_version(self):
        'Return the plugin version'
        return self._plugin_version
    @plugin_version.setter
    def plugin_version(self, value='0.0.1'):
        if not isinstance(value, str):
            raise TypeError
        self._plugin_version = value

    @property
    def parameters(self):
        'Return the list of parameters'
        return self._parameters
    @parameters.setter
    def parameters(self, value):
        self._parameters = value
