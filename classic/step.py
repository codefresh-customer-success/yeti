#!/usr/bin/env python3

#
# Classic Triggers
#

### IMPORTS ###
import logging
from .exceptions import StepTypeNotSupported
from .exceptions import VariableNotSupportedInField
### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Step:
    def __init__(self, name = None, block = None):

        self.logger = logging.getLogger(type(self).__name__)

        self.logger.debug("Step Name : %s", name)
        self.logger.debug("Step Block : %s", block)

        self.name = name
        self.type = block['type']
        self.image = block['image']
        self.commands = block['commands']
        self.cwd = block['working_directory']
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
    def type(self, value='freestyle'):
        if not isinstance(value, str):
            raise TypeError
        if not value == "freestyle":
            raise StepTypeNotSupported(value)
        self._type = value

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value = None):
        if not value:
            raise ImageRequired
        self._image = value

    @property
    def commands(self):
        return self._commands
    @commands.setter
    def commands(self, value = None):
        self._commands = value

    @property
    def cwd(self):
        return self._cwd
    @cwd.setter
    def cwd(self, value = '/codefresh/volume'):
        if value.contains('$'):
            raise VariableNotSupportedInField("working_directory")
        self._cwd = value
