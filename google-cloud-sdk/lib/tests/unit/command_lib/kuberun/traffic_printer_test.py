# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the traffic printer."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from googlecloudsdk.api_lib.kuberun import service
from googlecloudsdk.api_lib.run import traffic_pair as run_traffic_pair
from googlecloudsdk.command_lib.kuberun import traffic_pair
from googlecloudsdk.command_lib.kuberun import traffic_printer
from googlecloudsdk.command_lib.run import traffic_printer as run_traf_printer
from tests.lib.core.resource import resource_printer_test_base
from tests.lib.surface.kuberun import cloudrun_object_helpers as runhelpers

KUBERUN_SERVICE_TRAFFIC = service.Service({
    "spec": {
        "traffic": [
            {
                "revisionName": "rev1",
                "percent": 30,
                "tag": "tag1",
                "url": "rev1.service.example.com",
            },
            {
                "revisionName": "rev2",
                "latestRevision": False,
                "percent": 30,
                "tag": "tag2",
                "url": "rev2.service.example.com",
            },
            {
                "configurationName": "conf3",
                "latestRevision": True,
                "percent": 40,
                "tag": "tag3",
                "url": "conf3.service.example.com",
            },
        ]
    },
    "status": {
        "traffic": [
            {
                "revisionName": "rev1",
                "percent": 50,
                "tag": "tag1",
                "url": "rev1.service.example.com",
            },
            {
                "revisionName": "rev2",
                "latestRevision": False,
                "percent": 50,
                "tag": "tag2",
                "url": "rev2.service.example.com",
            },
        ],
    }
})


class TrafficPrinterTest(resource_printer_test_base.Base):

  def SetUp(self):
    self._printer = traffic_printer.TrafficPrinter()
    self.ShowTestOutput()

  def testEmptyDefault(self):
    self._printer.Finish()
    self.AssertOutputEquals("")

  def testTraffic_consistentWithCloudRun(self):
    spec_traffic = _run_spec_traffic()
    status_traffic = _run_status_traffic()
    run_traf = run_traffic_pair.GetTrafficTargetPairs(
        runhelpers.TrafficTargets(spec_traffic,
                                  runhelpers.TestMessagesModule()),
        runhelpers.TrafficTargets(status_traffic,
                                  runhelpers.TestMessagesModule()), False,
        "rev1", "service.example.com")
    run_printer = run_traf_printer.TrafficPrinter()
    run_printer.AddRecord(run_traf)
    run_printer.Finish()
    run_out = self.GetOutput()
    self.ClearOutput()

    kuberun_traf = traffic_pair.GetTrafficTargetPairs(
        KUBERUN_SERVICE_TRAFFIC.spec_traffic,
        KUBERUN_SERVICE_TRAFFIC.status_traffic, "rev1", "service.example.com")
    self._printer.AddRecord(kuberun_traf)
    self._printer.Finish()

    self.AssertOutputEquals(run_out)

  def testTransformTraffic_consistentWithCloudRun(self):

    run_spec_traffic = _run_spec_traffic()
    run_status_traffic = _run_status_traffic()
    run_traf = run_traf_printer.TransformTraffic(
        runhelpers.RunService(
            runhelpers.TestMessagesModule(),
            runhelpers.Metadata("svc", "default"),
            runhelpers.ServiceSpec(traffic=run_spec_traffic),
            runhelpers.ServiceStatus(traffic=run_status_traffic)))

    run_traf.Print(self.stdout, 0, run_traf.CalculateColumnWidths())
    run_out = self.GetOutput()
    self.ClearOutput()

    kuberun_traf = traffic_printer.TransformTraffic(KUBERUN_SERVICE_TRAFFIC)
    kuberun_traf.Print(self.stdout, 0, kuberun_traf.CalculateColumnWidths())
    self.AssertOutputEquals(run_out)


def _run_spec_traffic():
  return (runhelpers.TrafficTarget("rev1", 30, None, "tag1",
                                   "rev1.service.example.com"),
          runhelpers.TrafficTarget("rev2", 30, False, "tag2",
                                   "rev2.service.example.com"),
          runhelpers.TrafficTarget("conf3", 40, True, "tag3",
                                   "conf3.service.example.com"))


def _run_status_traffic():
  return (runhelpers.TrafficTarget("rev1", 50, None, "tag1",
                                   "rev1.service.example.com"),
          runhelpers.TrafficTarget("rev2", 50, False, "tag2",
                                   "rev2.service.example.com"))
