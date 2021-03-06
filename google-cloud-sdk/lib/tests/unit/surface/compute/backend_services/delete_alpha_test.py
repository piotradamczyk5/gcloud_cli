# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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
"""Tests for the backend-services delete subcommand."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.core import properties
from googlecloudsdk.core.resource import resource_projector
from tests.lib import completer_test_base
from tests.lib import test_case
from tests.lib.surface.compute import test_base
from tests.lib.surface.compute.backend_services import test_resources


class BackendServicesDeleteTest(test_base.BaseTest):

  def SetUp(self):
    self.SelectApi('alpha')
    self._backend_services = test_resources.BACKEND_SERVICES_ALPHA

  def testScopeWarning(self):
    properties.VALUES.core.disable_prompts.Set(True)
    self.Run("""
        alpha compute backend-services delete backend-service-1 --region alaska
        """)
    self.AssertErrNotContains('WARNING:')

  def testWithSingleBackendService(self):
    messages = self.messages
    properties.VALUES.core.disable_prompts.Set(True)
    self.Run("""
        alpha compute backend-services delete backend-service-1 --region alaska
        """)

    self.CheckRequests(
        [(self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-1',
              region='alaska',
              project='my-project'))],
    )

  def testWithManyBackendServices(self):
    messages = self.messages
    properties.VALUES.core.disable_prompts.Set(True)
    self.Run("""
        alpha compute backend-services delete backend-service-1 backend-service-2
          backend-service-3 --region alaska
        """)

    self.CheckRequests(
        [(self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-1',
              region='alaska',
              project='my-project')),

         (self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-2',
              region='alaska',
              project='my-project')),

         (self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-3',
              region='alaska',
              project='my-project'))],
    )

  def testPromptingWithYes(self):
    messages = self.messages
    self.WriteInput('y\n')
    self.Run("""
        alpha compute backend-services delete backend-service-1 backend-service-2
          backend-service-3 --region alaska
        """)

    self.CheckRequests(
        [(self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-1',
              region='alaska',
              project='my-project')),

         (self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-2',
              region='alaska',
              project='my-project')),

         (self.compute.regionBackendServices,
          'Delete',
          messages.ComputeRegionBackendServicesDeleteRequest(
              backendService='backend-service-3',
              region='alaska',
              project='my-project'))],
    )

  def testPromptingWithNo(self):
    self.WriteInput('n\n')
    with self.AssertRaisesToolExceptionRegexp('Deletion aborted by user.'):
      self.Run("""
          alpha compute backend-services delete backend-service-1 backend-service-2
            backend-service-3 --region alaska
          """)

    self.CheckRequests()


class BackendServicesDeleteCompletionTest(test_base.BaseTest,
                                          completer_test_base.CompleterBase):

  def testDeleteCompletion(self):
    self.ExpectListerInvoke(
        scope_set=self.MakeAllScopes(regional=True),
        result=resource_projector.MakeSerializable(
            test_resources.BACKEND_SERVICES_V1))
    self.ExpectListerInvoke(
        scope_set=self.MakeGlobalScope(),
        result=resource_projector.MakeSerializable(
            test_resources.BACKEND_SERVICES_V1))
    self.RunCompletion(
        'alpha compute backend-services delete b',
        ['backend-service-1', 'backend-service-2', 'backend-service-tcp'])


if __name__ == '__main__':
  test_case.main()
