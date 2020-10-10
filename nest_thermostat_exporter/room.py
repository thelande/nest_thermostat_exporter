# Copyright 2020 Thomas Helander
# All rights reserved.


class Room(object):
    def __init__(self, name, display_name):
        self._name = name
        self._display_name = display_name

    @property
    def structure_name(self):
        return "/".join(self.name.split("/")[0:4])

    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        return self._display_name

    def __repr__(self):
        return "<{}(display_name={})>".format(
            self.__class__.__name__, self.display_name
        )
