# Copyright 2020 Thomas Helander
# All rights reserved.
import click
import sys
from enum import IntEnum
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server
from .auth import get_authenticated_service
from .thermostat import Thermostat
from .util import make_metric

METRIC_G_CONNECTIVITY_STATUS = make_metric(
    "gauge", "connectivity_status", "Connectivity status"
)

METRIC_G_TEMPERATURE = make_metric(
    "gauge", "ambient_temperature_celsius", "Ambient temperature"
)

METRIC_G_ECO_COOL_SETPOINT = make_metric(
    "gauge", "eco_cool_setpoint_celsius", "Eco mode cooling setpoint"
)

METRIC_G_ECO_HEAT_SETPOINT = make_metric(
    "gauge", "eco_heat_setpoint_celsius", "Eco mode heating setpoint"
)
METRIC_G_COOL_SETPOINT = make_metric(
    "gauge", "cool_setpoint_celsius", "Cooling setpoint"
)
METRIC_G_HEAT_SETPOINT = make_metric(
    "gauge", "heat_setpoint_celsius", "Heating setpoint"
)
METRIC_G_HVAC_MODE = make_metric("gauge", "hvac_mode", "HVAC mode")
METRIC_G_HVAC_STATUS = make_metric("gauge", "hvac_status", "current HVAC status")


class Modes(IntEnum):
    OFF = 0
    HEAT = 1
    COOL = 2
    HEATCOOL = 3

    @classmethod
    def get_value(cls, s):
        if s == "OFF":
            return cls.OFF
        elif s == "HEAT" or s == "HEATING":
            return cls.HEAT
        elif s == "COOL" or s == "COOLING":
            return cls.COOL
        elif s == "HEATCOOL":
            return cls.HEATCOOL
        else:
            raise ValueError(f"Unknown mode: {s}")


def set_callbacks_for_thermostat(thermostat):
    labels = (
        thermostat.structure.custom_name,
        thermostat.room.display_name,
        thermostat.name,
    )

    METRIC_G_CONNECTIVITY_STATUS.labels(*labels).set_function(
        lambda: thermostat.connectivity_status == "ONLINE"
    )
    METRIC_G_HVAC_MODE.labels(*labels).set_function(
        lambda: Modes.get_value(thermostat.current_mode)
    )
    METRIC_G_ECO_COOL_SETPOINT.labels(*labels).set_function(
        lambda: thermostat.eco_cool_celsius
    )
    METRIC_G_ECO_HEAT_SETPOINT.labels(*labels).set_function(
        lambda: thermostat.eco_heat_celsius
    )
    METRIC_G_COOL_SETPOINT.labels(*labels).set_function(
        lambda: thermostat.setpoint_cool_celsius
    )
    METRIC_G_HEAT_SETPOINT.labels(*labels).set_function(
        lambda: thermostat.setpoint_heat_celsius
    )
    METRIC_G_TEMPERATURE.labels(*labels).set_function(
        lambda: thermostat.ambient_temperature_celsius
    )
    METRIC_G_HVAC_STATUS.labels(*labels).set_function(
        lambda: Modes.get_value(thermostat.hvac_status)
    )


@click.command()
@click.option(
    "--web.listen-address",
    "listen_address",
    default=":9810",
    type=str,
    help="Address on which to expose metrics and web interface.",
)
@click.option(
    "--config.client_secret",
    "client_secret",
    default="client_secret.json",
    type=str,
    help="Path to the Google client_secret.json file",
)
def main(listen_address, client_secret):
    addr, port = listen_address.split(":")

    try:
        enterprise = get_authenticated_service(client_secret)
    except InvalidGrantError:
        click.echo("Invalid authorization code", file=sys.stderr)
        sys.exit(1)

    thermostats = Thermostat.get_thermostats(enterprise)
    for thermostat in thermostats:
        set_callbacks_for_thermostat(thermostat)

    app = make_wsgi_app()
    httpd = make_server(addr, int(port), app)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
