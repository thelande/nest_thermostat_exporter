# Copyright 2020 Thomas Helander
# All rights reserved.
from pprint import pprint
from . import constants
from .parent import Parent


class ThermostatEco(object):
    def __init__(self, available_modes, cool_celsius, heat_celsius, mode):
        self._available_modes = available_modes
        self.cool_celsius = cool_celsius
        self.heat_celsius = heat_celsius
        self._mode = mode

    @property
    def available_modes(self):
        return self._available_modes

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in self.available_modes:
            raise ValueError(f"mode must be in {self.available_modes}")
        self._mode = value


class Thermostat(object):
    def __init__(
        self,
        raw_data,
        name,
        parents,
        connectivity_status,
        fan_timer_mode,
        ambient_humidity_percent,
        custom_name,
        temperature_scale,
        ambient_temperature_celsius,
        thermostat_eco,
        thermostat_hvac_status,
        thermostat_available_modes,
        thermostat_mode,
        thermostat_temperature_setpoint_cool_celsius,
        thermostat_temperature_setpoint_heat_celsius,
    ):
        self._raw_data = raw_data
        self._name = name
        self._parents = parents
        self._connectivity_status = connectivity_status
        self._fan_timer_mode = fan_timer_mode
        self._ambient_humidity_percent = ambient_humidity_percent
        self._custom_name = custom_name
        self._temperature_scale = temperature_scale
        self._ambient_temperature_celsius = ambient_temperature_celsius
        self._thermostat_eco = thermostat_eco
        self._thermostat_hvac_status = thermostat_hvac_status
        self._thermostat_available_modes = thermostat_available_modes
        self._thermostat_mode = thermostat_mode
        self._thermostat_temperature_setpoint_cool_celsius = (
            thermostat_temperature_setpoint_cool_celsius
        )
        self._thermostat_temperature_setpoint_heat_celsius = (
            thermostat_temperature_setpoint_heat_celsius
        )

    @classmethod
    def from_resource(cls, r):
        traits = r["traits"]
        eco = ThermostatEco(
            traits[constants.TRAITS_PREFIX + ".ThermostatEco"]["availableModes"],
            traits[constants.TRAITS_PREFIX + ".ThermostatEco"]["coolCelsius"],
            traits[constants.TRAITS_PREFIX + ".ThermostatEco"]["heatCelsius"],
            traits[constants.TRAITS_PREFIX + ".ThermostatEco"]["mode"],
        )

        parents = []
        for parent in r["parentRelations"]:
            parents.append(Parent(parent["displayName"], parent["parent"]))

        return Thermostat(
            r,
            r["name"].split("/")[-1],
            parents,
            traits[constants.TRAITS_PREFIX + ".Connectivity"]["status"],
            traits[constants.TRAITS_PREFIX + ".Fan"]["timerMode"],
            traits[constants.TRAITS_PREFIX + ".Humidity"]["ambientHumidityPercent"],
            traits[constants.TRAITS_PREFIX + ".Info"]["customName"],
            traits[constants.TRAITS_PREFIX + ".Settings"]["temperatureScale"],
            traits[constants.TRAITS_PREFIX + ".Temperature"][
                "ambientTemperatureCelsius"
            ],
            eco,
            traits[constants.TRAITS_PREFIX + ".ThermostatHvac"]["status"],
            traits[constants.TRAITS_PREFIX + ".ThermostatMode"]["availableModes"],
            traits[constants.TRAITS_PREFIX + ".ThermostatMode"]["mode"],
            traits[constants.TRAITS_PREFIX + ".ThermostatTemperatureSetpoint"].get(
                "coolCelsius"
            ),
            traits[constants.TRAITS_PREFIX + ".ThermostatTemperatureSetpoint"].get(
                "heatCelsius"
            ),
        )

    def running(self):
        """
        Returns True if the thermostat is currently running (heating, cooling, or fan
        running).

        :rtype: bool
        """
        return (
            self.fan_timer_mode == constants.STATE_ON
            or self.thermostat_mode != constants.STATE_OFF
        )

    def dump(self):
        """
        Dumps this devices' raw data to the console.
        """
        pprint(self._raw_data)

    def __repr__(self):
        return "<{}(parent={}, name={})>".format(
            self.__class__.__name__, self.parent, self.name
        )

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parents[0]

    @property
    def connectivity_status(self):
        return self._connectivity_status

    @property
    def fan_timer_mode(self):
        return self._fan_timer_mode

    @property
    def ambient_humidity_percent(self):
        return self._ambient_humidity_percent

    @property
    def custom_name(self):
        return self._custom_name

    @property
    def temperature_scale(self):
        return self._temperature_scale

    @property
    def ambient_temperature_celsius(self):
        return self._ambient_temperature_celsius

    @property
    def thermostat_eco(self):
        return self._thermostat_eco

    @property
    def thermostat_hvac_status(self):
        return self._thermostat_hvac_status

    @property
    def thermostat_available_modes(self):
        return self._thermostat_available_modes

    @property
    def thermostat_mode(self):
        return self._thermostat_mode

    @property
    def setpoint_cool_celsius(self):
        return self._thermostat_temperature_setpoint_cool_celsius

    @property
    def setpoint_heat_celsius(self):
        return self._thermostat_temperature_setpoint_heat_celsius
