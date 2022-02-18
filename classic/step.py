#!/usr/bin/env python3
'''Super class for a step with common fields'''

### IMPORTS ###
import logging

### GLOBALS ###

### FUNCTIONS ###


### CLASSES ###
class Step:
    '''Super class for step'''
    def __init__(self, name, stype, fail_fast):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Creating New Step: %s", name)

        self.name = name
        self.type = stype
        self.fail_fast = fail_fast

    #
    # Setters and getters
    #
    @property
    def name(self):
        'Return the name of the step'
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
        '''Return the step type'''
        return self._type
    @type.setter
    def type(self, value):
        self._type = value

    @property
    def fail_fast(self):
        '''Return the step fail_fast'''
        return self._fail_fast
    @fail_fast.setter
    def fail_fast(self, value):
        self._fail_fast = value
