# Copyright 2020 Thomas Helander
# All rights reserved.
from prometheus_client import Counter, Enum, Gauge, Info, Summary
from .constants import LABELS, METRIC_PREFIX


def c_to_f(t):
    if t == "NaN":
        return t
    return t * 9 / 5 + 32.0


def make_metric(metric_type, name, description, **kwargs):
    """
    Creates a Prometheus metric.

    :param str metric_type:
    :param str name:
    :param str description:
    :rtype: prometheus_client.metrics.MetricWrapperBase
    """
    if metric_type == "counter":
        klass = Counter
    elif metric_type == "gauge":
        klass = Gauge
    elif metric_type == "info":
        klass = Info
    elif metric_type == "enum":
        klass = Enum
    elif metric_type == "summary":
        klass = Summary
    else:
        raise ValueError(f"Unknown metric type: {metric_type}")

    return klass(METRIC_PREFIX + f"_{name}", description, labelnames=LABELS, **kwargs,)
