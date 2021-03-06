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

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from tests.lib import test_case
from tests.lib.surface.compute.backend_services import test_resources
from tests.lib.surface.compute.backend_services.update import test_base


class BackendServiceWithConnectionDrainingTimeoutApiUpdateTest(
    test_base.BetaUpdateTestBase):

  def SetUp(self):
    self._backend_services_with_connection_draining_timeout = (
        test_resources.MakeBackendServicesWithConnectionDrainingTimeout(
            self.messages, 'beta'))

  def testUnchanged(self):
    messages = self.messages
    self.make_requests.side_effect = iter([
        [self._backend_services_with_connection_draining_timeout[0]],
        [],
    ])

    self.RunUpdate('backend-service-1 --description "whatever"')

    self.CheckRequests(
        [(self.compute.backendServices, 'Get',
          messages.ComputeBackendServicesGetRequest(
              backendService='backend-service-1', project='my-project'))],
        [(self.compute.backendServices, 'Patch',
          messages.ComputeBackendServicesPatchRequest(
              backendService='backend-service-1',
              backendServiceResource=messages.BackendService(
                  backends=[],
                  description='whatever',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check')
                  ],
                  name='backend-service-1',
                  portName='http',
                  protocol=messages.BackendService.ProtocolValueValuesEnum.HTTP,
                  selfLink=(self.compute_uri + '/projects/'
                            'my-project/global/backendServices/'
                            'backend-service-1'),
                  connectionDraining=messages.ConnectionDraining(
                      drainingTimeoutSec=120)),
              project='my-project'))],
    )

  def testChangeConnectionDrainingTimeout(self):
    messages = self.messages
    self.make_requests.side_effect = iter([
        [self._backend_services_with_connection_draining_timeout[0]],
        [],
    ])

    self.RunUpdate('backend-service-1 '
                   '--description "whatever" '
                   '--connection-draining-timeout 300')

    self.CheckRequests(
        [(self.compute.backendServices, 'Get',
          messages.ComputeBackendServicesGetRequest(
              backendService='backend-service-1', project='my-project'))],
        [(self.compute.backendServices, 'Patch',
          messages.ComputeBackendServicesPatchRequest(
              backendService='backend-service-1',
              backendServiceResource=messages.BackendService(
                  backends=[],
                  description='whatever',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check')
                  ],
                  name='backend-service-1',
                  portName='http',
                  protocol=messages.BackendService.ProtocolValueValuesEnum.HTTP,
                  selfLink=(self.compute_uri + '/projects/'
                            'my-project/global/backendServices/'
                            'backend-service-1'),
                  connectionDraining=messages.ConnectionDraining(
                      drainingTimeoutSec=300)),
              project='my-project'))],
    )

  def testChangeConnectionDrainingTimeoutInMinutes(self):
    messages = self.messages
    self.make_requests.side_effect = iter([
        [self._backend_services_with_connection_draining_timeout[0]],
        [],
    ])

    self.RunUpdate('backend-service-1 '
                   '--description "whatever" '
                   '--connection-draining-timeout 5m')

    self.CheckRequests(
        [(self.compute.backendServices, 'Get',
          messages.ComputeBackendServicesGetRequest(
              backendService='backend-service-1', project='my-project'))],
        [(self.compute.backendServices, 'Patch',
          messages.ComputeBackendServicesPatchRequest(
              backendService='backend-service-1',
              backendServiceResource=messages.BackendService(
                  backends=[],
                  description='whatever',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check')
                  ],
                  name='backend-service-1',
                  portName='http',
                  protocol=messages.BackendService.ProtocolValueValuesEnum.HTTP,
                  selfLink=(self.compute_uri + '/projects/'
                            'my-project/global/backendServices/'
                            'backend-service-1'),
                  connectionDraining=messages.ConnectionDraining(
                      drainingTimeoutSec=300)),
              project='my-project'))],
    )


if __name__ == '__main__':
  test_case.main()
