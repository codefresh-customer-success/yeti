#!/usr/bin/env python3
'''Implenetaion of step conditions'''

### IMPORTS ###
import logging

### GLOBALS ###

### FUNCTIONS ###


### CLASSES ###
class Condition:
    'Condition class for step'
    def __init__(self, block) -> None:
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Creating New Condition: %s", block)

    if  not 'steps' in block:
        self.logger.warning("only conditions on step state supported")
    
    for cond in block['steps']:
        self.step_name=cond.name
        for on_line in cond['on']
            self.