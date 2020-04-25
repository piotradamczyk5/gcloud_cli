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
"""Tests for `gcloud access-context-manager perimeters dry-run drop`."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.command_lib.accesscontextmanager import perimeters
from googlecloudsdk.core import properties
from tests.lib import cli_test_base
from tests.lib import test_case
from tests.lib.surface import accesscontextmanager


class DryRunEnforceTestBeta(accesscontextmanager.Base):

  def PreSetUp(self):
    self.api_version = 'v1'
    self.track = calliope_base.ReleaseTrack.BETA

  def SetUp(self):
    properties.VALUES.core.user_output_enabled.Set(False)

  def _GetPerimeterType(self, kind):
    return perimeters.GetPerimeterTypeEnumForShortName(kind, self.api_version)

  def _ExpectGet(self, perimeter):
    m = self.messages
    get_req_type = (
        m.AccesscontextmanagerAccessPoliciesServicePerimetersGetRequest)
    self.client.accessPolicies_servicePerimeters.Get.Expect(
        get_req_type(name=perimeter.name), perimeter)

  def _ExpectPatch(self, perimeter_name, perimeter_update, perimeter_after,
                   update_mask):
    m = self.messages
    req_type = m.AccesscontextmanagerAccessPoliciesServicePerimetersPatchRequest
    self.client.accessPolicies_servicePerimeters.Patch.Expect(
        req_type(
            name=perimeter_name,
            servicePerimeter=perimeter_update,
            updateMask=update_mask),
        self.messages.Operation(name='operations/my-op', done=False))
    self._ExpectGetOperation('operations/my-op')
    self._ExpectGet(perimeter_after)

  def testEnforce_PerimeterNameMissing(self):
    self.SetUpForAPI(self.api_version)
    with self.AssertRaisesExceptionMatches(cli_test_base.MockArgumentError,
                                           'must be specified'):
      self.Run('access-context-manager perimeters dry-run enforce --policy 123')

  def testEnforce(self):
    self.SetUpForAPI(self.api_version)
    perimeter_before = self.messages.ServicePerimeter(
        name='accessPolicies/123/servicePerimeters/MY_PERIMETER',
        title='My Perimeter Title',
        perimeterType=self._GetPerimeterType('regular'),
        description='foo',
        status=None,
        useExplicitDryRunSpec=True,
        spec=self.messages.ServicePerimeterConfig(resources=['projects/123']))
    perimeter_update = self.messages.ServicePerimeter(
        useExplicitDryRunSpec=False,
        spec=None,
        status=self.messages.ServicePerimeterConfig(resources=['projects/123']))
    perimeter_after = self.messages.ServicePerimeter(
        name='accessPolicies/123/servicePerimeters/MY_PERIMETER',
        title='My Perimeter Title',
        perimeterType=self._GetPerimeterType('regular'),
        description='foo',
        useExplicitDryRunSpec=False,
        spec=None,
        status=self.messages.ServicePerimeterConfig(resources=['projects/123']))
    self._ExpectGet(perimeter_before)
    self._ExpectPatch('accessPolicies/123/servicePerimeters/MY_PERIMETER',
                      perimeter_update, perimeter_after,
                      'spec,status,useExplicitDryRunSpec')

    result = self.Run(
        'access-context-manager perimeters dry-run enforce MY_PERIMETER '
        '   --policy 123')

    self.assertEqual(result, perimeter_after)


class DryRunEnforceTestAlpha(DryRunEnforceTestBeta):

  def PreSetUp(self):
    self.api_version = 'v1alpha'
    self.track = calliope_base.ReleaseTrack.ALPHA


if __name__ == '__main__':
  test_case.main()