#!/usr/bin/env python3
'''Super class for a step with common fields'''

### IMPORTS ###
import logging
import re

### GLOBALS ###

### FUNCTIONS ###
def grab_field_value(block, field, default_value):
    '''Return the field value from the yaml block if it exists 
       or return the default valye'''
    value=default_value
    if field in block:
        value=block[field]
    return value

def replace_parameter_variable_by_step_output(value, output):
    '''replace ${{}} reference from a field to the correct output from a previous step
       - a clone step, will return a WORKING_DIR to be use as a working_dir
       - build step will return an IMAGE
    '''
    if '$' in value:
        # replace value of variable in working by output of named step
        regexp = r"\$\{{1,2}([^}]+)\}{1,2}"

        #
        # TODO:
        #  - add check to confirm this macthes a step name
        subst="{{ tasks.\\1.outputs.parameters.%s }}" %(output)
        # logging.debug("replaceParameterVariableByStepOutput - subst: %s", subst)
        value=re.sub(regexp, subst,value,0)
    return value

### CLASSES ###
class Step:
    '''Super class for step'''
    def __init__(self, name, stype, block):

        cwd=grab_field_value(block, "working_directory", "/codefresh/volume")
        cwd=replace_parameter_variable_by_step_output(cwd, "WORKING_DIR")
        fail_fast=grab_field_value(block, "fail_fast", "false")

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
