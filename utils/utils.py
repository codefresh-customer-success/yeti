#!/usr/bin/env python3
'''
    Set of misc utilities functions
'''
### IMPORTS ###
import string

### GLOBALS ###

### FUNCTIONS ###
def safeName (name):
    '''Return a kubernetes valid string'''
    if not isinstance(name, str):
        raise TypeError 
   return name.replace('/','__').lower()

### CLASSES ###
