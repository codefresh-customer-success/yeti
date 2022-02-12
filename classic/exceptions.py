#!/usr/bin/env python3

### IMPORTS ###

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ManifestMissingValueException(Exception):
    pass
class ManifestEmptyException(Exception):
    pass
class InvalidYamlAsPipeline(Exception):
    pass
class OnlySupportGitTriggerException(Exception):
    pass
class OnlySupportGithubProvider(Exception):
    pass

class ParallelModeNotSupported(Exception):
    pass

class EmptyObjectException(Exception):
    pass
