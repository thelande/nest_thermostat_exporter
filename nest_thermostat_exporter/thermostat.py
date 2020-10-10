# Copyright 2020 Thomas Helander
# All rights reserved.
from datetime import datetime, timedelta
from pprint import pprint
from .constants import ENTERPRISE_NAME, THERMOSTAT_TYPE, TRAITS_PREFIX
from .room import Room
from .structure import Structure
from .util import c_to_f


class Thermostat(object):
    # Minimum allowed time between refreshes in seconds
    REFRESH_LIMIT = timedelta(seconds=15)

    def __init__(self, enterprise, name, parent_rels, traits):
        self._enterprise = enterprise
        self._structure = None
        self._room = None
        self._name = name
        self._traits = traits
        self._last_refresh = None

        self.set_parents(parent_rels)

    @classmethod
    def get_thermostats(cls, enterprise):
        resp = enterprise.devices().list(parent=ENTERPRISE_NAME).execute()
        resources = resp.get("devices")
        if resources is None:
            raise ValueError("Invalid response: no devices key")

        thermostats = []
        for res in resources:
            dev_type = res["type"]
            if dev_type != THERMOSTAT_TYPE:
                continue

            name = res["name"]
            traits = res["traits"]
            parent_rels = res["parentRelations"]
            thermostats.append(Thermostat(enterprise, name, parent_rels, traits))

        return thermostats

    def set_parents(self, parent_rels):
        for rel in parent_rels:
            name = rel["parent"]
            display_name = rel["displayName"]

            if "room" in name:
                # Is a room, get the room and structure
                self._room = Room(name, display_name)

                req = self._enterprise.structures().get(name=self._room.structure_name)
                resp = req.execute()
                self._structure = Structure(
                    self._enterprise,
                    resp["name"],
                    resp["traits"]["sdm.structures.traits.Info"]["customName"],
                )
            elif "structure" in name:
                # Is a structure
                self._structure = Structure(self._enterprise, name, display_name)
            else:
                raise ValueError("parent is neither structure nor room")

    def refresh_traits(self):
        if (
            self._last_refresh is None
            or self._last_refresh + self.REFRESH_LIMIT < datetime.now()
        ):
            resp = self._enterprise.devices().get(name=self.name).execute()
            self._traits = resp["traits"]
            self._last_refresh = datetime.now()

    def _get_trait_value(self, trait, key, default=None):
        return self._traits[TRAITS_PREFIX + "." + trait].get(key, default)

    def dump_traits(self):
        pprint(self._traits)

    def __repr__(self):
        return "<{}(structure={}, room={}, name={})>".format(
            self.__class__.__name__,
            self.structure.custom_name if self.structure else None,
            self.room.display_name if self.room else None,
            self.name,
        )

    @property
    def room(self):
        return self._room

    @property
    def structure(self):
        return self._structure

    @property
    def name(self):
        return self._name

    @property
    def connectivity_status(self):
        self.refresh_traits()
        return self._get_trait_value("Connectivity", "status")

    @property
    def fan_timer_mode(self):
        self.refresh_traits()
        return self._get_trait_value("Fan", "timerMode")

    @property
    def fan_timer_timeout(self):
        self.refresh_traits()
        return self._get_trait_value("Fan", "timerTimeout")

    @property
    def ambient_humidity_percent(self):
        self.refresh_traits()
        return self._get_trait_value("Humidity", "ambientHumidityPercent")

    @property
    def custom_name(self):
        self.refresh_traits()
        return self._get_trait_value("Info", "customName")

    @property
    def temperature_scale(self):
        self.refresh_traits()
        return self._get_trait_value("Settings", "temperatureScale")

    @property
    def ambient_temperature_celsius(self):
        self.refresh_traits()
        return self._get_trait_value("Temperature", "ambientTemperatureCelsius")

    @property
    def ambient_temperature_fahrenheit(self):
        self.refresh_traits()
        return c_to_f(self.ambient_temperature_celsius)

    @property
    def eco_available_modes(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatEco", "availableModes")

    @property
    def eco_current_modes(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatEco", "mode")

    @property
    def eco_heat_celsius(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatEco", "heatCelsius", "NaN")

    @property
    def eco_heat_fahrenheit(self):
        return c_to_f(self.eco_heat_celsius)

    @property
    def eco_cool_celsius(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatEco", "coolCelsius", "NaN")

    @property
    def eco_cool_fahrenheit(self):
        return c_to_f(self.eco_cool_celsius)

    @property
    def hvac_status(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatHvac", "status")

    @property
    def available_modes(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatMode", "availableModes")

    @property
    def current_mode(self):
        self.refresh_traits()
        return self._get_trait_value("ThermostatMode", "mode")

    @property
    def setpoint_heat_celsius(self):
        self.refresh_traits()
        return self._get_trait_value(
            "ThermostatTemperatureSetpoint", "heatCelsius", "NaN"
        )

    @property
    def setpoint_heat_fahrenheit(self):
        return c_to_f(self.setpoint_heat_celsius)

    @property
    def setpoint_cool_celsius(self):
        self.refresh_traits()
        return self._get_trait_value(
            "ThermostatTemperatureSetpoint", "coolCelsius", "NaN"
        )

    @property
    def setpoint_cool_fahrenheit(self):
        return c_to_f(self.setpoint_cool_celsius)
