#!/usr/bin/env python3

#
# Classic Triggers
#

### IMPORTS ###
import logging
from .exceptions import StepTypeNotSupported
from .exceptions import VariableNotSupportedInField
from .exceptions import  ShellTypeNotSupported
### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Step:
    def __init__(self, name = None, block = None):

        self.logger = logging.getLogger(type(self).__name__)

        self.logger.debug("Creating New Step: %s", name)

        self.name = name
        self._type="freestyle"
        if 'type' in block:
            self.type = block['type']

        self._shell="sh"
        if 'shell' in block:
            self.shell = block['shell']

        self.image = block['image']
        self.commands = block['commands']

        self._cwd='/codefresh/volume'
        if 'working_directory' in block:
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
    def type(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value == "freestyle":
            raise StepTypeNotSupported(value)
        self._type = value

    @property
    def shell(self):
        return self._shell
    @shell.setter
    def shell(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value in ["sh", "bash"]:
            raise ShellTypeNotSupported(value)
        self._shell = value

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
    def cwd(self, value):
        if '$' in value:
            raise VariableNotSupportedInField("working_directory")
        self._cwd = value
