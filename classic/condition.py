#!/usr/bin/env python3
'''Implenetaion of step conditions'''

### IMPORTS ###
import logging
from .exceptions import ConditionStateNotSupported
from .exceptions import OnlyStepConditionsSupported

### GLOBALS ###


### FUNCTIONS ###

def create_conditions_for_a_step(block):
    'Parse the when block to create an array of conditions'
    logging.debug("Conditions: %s", block)
    conditions=[]
    if  not 'steps' in block:
        raise OnlyStepConditionsSupported()
    
    for cond in block['steps']:
        step_name=cond['name']
        for state in cond['on']:
            conditions.append(Condition(step_name, state))
    return conditions

### CLASSES ###
class Condition:
    'Condition class for step'
    def __init__(self, step_name, state) -> None:
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Creating New Condition: %s (%s)", step_name, state)

        self.step_name=step_name
        self.state=state

    #
    # Setters and getters
    #
    @property
    def state(self):
        'Return the state condition aka success, failure, finished, ...'
        return self._state
    @state.setter
    def state(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value in ["success", "failure", "finished"]:
            raise ConditionStateNotSupported(value)
        self._state=value