# Copyright 2020 Thomas Helander
# All rights reserved.


class Parent(object):
    def __init__(self, display_name, parent):
        self._display_name = display_name
        self._parent = parent

    @property
    def display_name(self):
        return self._display_name

    @property
    def parent(self):
        return self._parent

    def __repr__(self):
        return "<{}(display_name={})>".format(
            self.__class__.__name__, self.display_name
        )
