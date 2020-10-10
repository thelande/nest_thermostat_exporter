# Copyright 2020 Thomas Helander
# All rights reserved.
from .constants import ENTERPRISE_NAME, TRAITS_PREFIX


class Structure(object):
    def __init__(self, enterprise, name, custom_name):
        self._enterprise = enterprise
        self._name = name
        self._custom_name = custom_name

    @classmethod
    def get_structures(cls, enterprise):
        resp = enterprise.structures().list(parent=ENTERPRISE_NAME).execute()
        resources = resp.get("structures")
        if resources is None:
            raise ValueError("Invalid response: no structures key")

        structures = []
        for res in resources:
            name = res["name"]
            traits = res["traits"]
            custom_name = traits.get(TRAITS_PREFIX + ".Info", {}).get("customName")
            structures.append(Structure(enterprise, name, custom_name))

        return structures

    def get_rooms(self):
        resp = self._enterprise.structures().rooms().list(parent=self.name).execute()
        resources = resp.get("rooms")

    @property
    def name(self):
        return self._name

    @property
    def custom_name(self):
        return self._custom_name
