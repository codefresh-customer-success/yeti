#!/usr/bin/env python3

#
# Classic Triggers
#

### IMPORTS ###
import logging
import re

from .step       import Step
from .exceptions import VariableNotSupportedInField
### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Freestyle(Step):
    def __init__(self, name, shell, image, cwd, commands):
        self.logger = logging.getLogger(type(self).__name__)

        super().__init__(name, "freestyle" )
        self.image=image
        self.cwd=cwd
        self.commands=commands
        self.shell=shell

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
        str=""
        for line in value:
            str += f"      {line}\n"
        self._commands=str

    @property
    def cwd(self):
        return self._cwd
    @cwd.setter
    def cwd(self, value):
        if '$' in value:
            # replace value of variable in working by output of named step
            regexp = r"\$\{{1,2}([^}]+)\}{1,2}"
            subst="{{tasks.\\1.outputs.parameters.WORKING_DIR}}"
            value=re.sub(regexp, subst,value,0)
        self._cwd = value

    @property
    def shell(self):
        return self._shell
    @shell.setter
    def shell(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value in ["sh", "bash"]:
            raise ShellTypeNotSupported(value)
        self._shell = f"[{value}]"
