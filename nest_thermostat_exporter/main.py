# Copyright 2020 Thomas Helander
# All rights reserved.
import click
import sys
from datetime import datetime, timedelta
from functools import partial
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from prometheus_client import make_wsgi_app, Gauge
from wsgiref.simple_server import make_server
from .auth import get_authenticated_service
from .thermostat import Thermostat

METRIC_PREFIX = "nest_thermostat"
PROJECT_ID = "a88b302d-d075-401f-90ec-7d911ce301c9"

THERMOSTAT_TYPE = "sdm.devices.types.THERMOSTAT"

DEVICE_CACHE = {}
CACHE_SECONDS = 15

METRIC_LABELS = ["location", "device_id"]


def _get_device_from_cache(device_id):
    if device_id in DEVICE_CACHE:
        if DEVICE_CACHE[device_id]["expires_at"] > datetime.now():
            return DEVICE_CACHE[device_id]["device"]
        DEVICE_CACHE.pop(device_id)
    return None


def _add_device_to_cache(device):
    DEVICE_CACHE[device.name] = {
        "device": device,
        "expires_at": datetime.now() + timedelta(seconds=CACHE_SECONDS),
    }
    # print(f"Added {device.name} to cache for {CACHE_SECONDS} seconds.")


def _get_devices(service):
    return (
        service.devices()
        .list(parent=f"enterprises/{PROJECT_ID}")
        .execute()
        .get("devices")
    )


def _get_thermostats(service):
    devices = _get_devices(service)
    # pp.pprint(devices)
    return [
        Thermostat.from_resource(dev)
        for dev in devices
        if dev["type"] == THERMOSTAT_TYPE
    ]


def _get_thermostat(service, device_id):
    device = _get_device_from_cache(device_id)
    if device is None:
        # print(f"Thermostat {device_id} not in cache, fetching...")
        resp = (
            service.devices()
            .get(name=f"enterprises/{PROJECT_ID}/devices/{device_id}")
            .execute()
        )
        device = Thermostat.from_resource(resp)
        _add_device_to_cache(device)
    return device


def _get_temperature_celsius(service, device_id):
    device = _get_thermostat(service, device_id)
    return device.ambient_temperature_celsius


def _get_eco_cool_celsius(service, device_id):
    device = _get_thermostat(service, device_id)
    return device.thermostat_eco.cool_celsius


def _get_eco_heat_celsius(service, device_id):
    device = _get_thermostat(service, device_id)
    return device.thermostat_eco.heat_celsius


def _get_setpoint_cool_celsius(service, device_id):
    device = _get_thermostat(service, device_id)
    return device.setpoint_cool_celsius or 0


def _get_setpoint_heat_celsius(service, device_id):
    device = _get_thermostat(service, device_id)
    return device.setpoint_heat_celsius or 0


def _get_humidity(service, device_id):
    device = _get_thermostat(service, device_id)
    return device.ambient_humidity_percent


def _get_connectivity(service, device_id):
    device = _get_thermostat(service, device_id)
    return 1 if device.connectivity_status else 0


def _get_running(service, device_id):
    device = _get_thermostat(service, device_id)
    return 1 if device.running else 0


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
        service = get_authenticated_service(client_secret)
    except InvalidGrantError:
        click.echo("Invalid authorization code", file=sys.stderr)
        sys.exit(1)

    devices = _get_thermostats(service)

    # Set up metrics
    g_temp = Gauge(METRIC_PREFIX + "_temperature_celsius", "Temperature", METRIC_LABELS)
    g_eco_cool = Gauge(METRIC_PREFIX + "_eco_cool_celsius", "Eco mode cooling temperature", METRIC_LABELS)
    g_eco_heat = Gauge(METRIC_PREFIX + "_eco_heat_celsius", "Eco mode heating temperature", METRIC_LABELS)
    g_setpoint_cool = Gauge(METRIC_PREFIX + "_setpoint_cool_celsius", "Cooling setpoint temperatures", METRIC_LABELS)
    g_setpoint_heat = Gauge(METRIC_PREFIX + "_setpoint_heat_celsius",
                            "Heating setpoint temperatures", METRIC_LABELS)
    g_hum = Gauge(
        METRIC_PREFIX + "_humidity_percent", "Relative humidity", METRIC_LABELS,
    )
    g_connectivity = Gauge(
        METRIC_PREFIX + "_connectivity_state",
        "Current connectivity state",
        METRIC_LABELS,
    )
    # g_running = Gauge(
    #     METRIC_PREFIX + "_running_state",
    #     "Is the system currently cooling, heating, or running the fan?",
    #     METRIC_LABELS
    # )

    # Set up callbacks
    for dev in devices:
        location = dev.parent.display_name
        device_id = dev.name

        g_temp.labels(location, device_id).set_function(
            partial(_get_temperature_celsius, service, device_id)
        )

        g_eco_cool.labels(location, device_id).set_function(
            partial(_get_eco_cool_celsius, service, device_id)
        )

        g_eco_heat.labels(location, device_id).set_function(
            partial(_get_eco_heat_celsius, service, device_id)
        )

        g_setpoint_cool.labels(location, device_id).set_function(
            partial(_get_setpoint_cool_celsius, service, device_id)
        )

        g_setpoint_heat.labels(location, device_id).set_function(
            partial(_get_setpoint_heat_celsius, service, device_id)
        )

        g_hum.labels(location, device_id).set_function(
            partial(_get_humidity, service, device_id)
        )

        g_connectivity.labels(location, device_id).set_function(
            partial(_get_connectivity, service, device_id)
        )

        # g_running.labels(location, device_id).set_function(
        #     partial(_get_running, service, device_id)
        # )

    app = make_wsgi_app()
    httpd = make_server(addr, int(port), app)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
