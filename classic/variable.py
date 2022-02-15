#!/usr/bin/env python3

### IMPORTS ###
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Variable:
    def __init__(self, name, value, source, order, path):
        self.logger = logging.getLogger(type(self).__name__)

        self.logger.debug("Adding variable %s (%s) from %s #%d",
            name, value, source, order)
        self.name = name            # Name
        self.value = value          # value
        self.source = source        # project, pipeline, ....
        self.order = order          # for position in Argo as itdoes not support by name
        self._path = path             # event source payload path

# setters and getters
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

    # order of the parameter as workflow don't support name
    @property
    def order(self):
        return self._order
    @order.setter
    def order(self, value):
        if not isinstance(value, int):
            raise TypeError
        if value < 0:
            raise ValueError
        self._order = value

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, val):
        self._value = val

    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, value):
        if not value in ["pipeline", "system"]:
            raise VariableSourceNotSupported(value)
        self._source = value

    # Path from the EventSource payload
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, val):
        self._path = val
