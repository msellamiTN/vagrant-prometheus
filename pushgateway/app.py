#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals
from django.conf import settings

import prometheus_client
from prometheus_client import (
    CollectorRegistry,
    Gauge,
)

"""
Short lived batch jobs are monitored via push rather than pull.
see this for details, https://prometheus.io/docs/instrumenting/pushing/

Example

@PopulateDevicesMetric.monitor
def run_job_that_parses_pciids():
    pass
"""


class PopulateDevicesMetric(object):
    success = Gauge("populate_devices_last_success_unixtime", "Last time the populate_devices job ran successfully.")
    failure = Gauge("populate_devices_last_failure_unixtime", "Last time the populate_devices job failed.")
    duration = Gauge("populate_devices_duration_seconds", "The number of seconds to complete the populate_devices job.")
    added = Gauge("populate_devices_added_count", "Count of added devices or vendors", ["item_type"])
    updated = Gauge("populate_devices_updated_count", "Count of updated devices or vendors", ["item_type"])

    enabled = True
    pushgateway = "localhost:9091"

    registry = CollectorRegistry()
    registry.register(success)
    registry.register(failure)
    registry.register(duration)
    registry.register(added)
    registry.register(updated)

    @classmethod
    def push_to_gateway(cls):
        if cls.enabled:
            prometheus_client.push_to_gateway(cls.pushgateway, job='pushgateway', registry=cls.registry)

    @classmethod
    def monitor(cls, f):
        """
        Monitors the last known success or failure time
        """
        def current_time(*args, **kwargs):
            try:
                with cls.duration.time():
                    result = f(*args, **kwargs)
                cls.success.set_to_current_time()
                cls.count_devices_processed(result)
                return result
            except:
                cls.failure.set_to_current_time()
                raise
            finally:
                cls.push_to_gateway()
        return current_time

    @classmethod
    def count_devices_processed(cls, stats):
        """
        Pushes the results for updated/added devices and vendors from a DevicePopulator run.
        """
        # do a minimal sanity check before trying to access things in the resulting stats
        if not stats or not isinstance(stats, dict):
            return

        try:
            """
            expected stats format::
            
                {
                'pci': {'new': 0, 'updated': 0},
                'usb': {'new': 0, 'updated': 0},
                'vendors': {'new': 0, 'updated': 0}
                }
            """
            for item_type, counts in stats.iteritems():
                cls.added.labels(item_type=item_type).set(counts.get("new", 0))
                cls.updated.labels(item_type=item_type).set(counts.get("updated", 0))
            cls.push_to_gateway()

        except Exception:
            # TODO what action will we want to take here?
            raise  # ignore? fallback to logging? just re-raise for now.

PopulateDevicesMetric.pushgateway = getattr(settings, "PROMETHEUS_PUSHGATEWAY", "localhost:9091")
PopulateDevicesMetric.enabled = getattr(settings, "PROMETHEUS_ENABLED", False)
