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

"""Unit tests for the intance_utils module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import managed_instance_groups_utils
from googlecloudsdk.api_lib.util import apis as core_apis
from googlecloudsdk.calliope import base as calliope_base
from tests.lib import cli_test_base
from tests.lib import sdk_test_base
from tests.lib import test_case


class ManagesInstanceGroupUtilsTest(cli_test_base.CliTestBase,
                                    sdk_test_base.WithFakeAuth):

  def SetUp(self):
    self.messages = core_apis.GetMessagesModule('compute', 'alpha')
    self.resources = base_classes.ComputeApiHolder(calliope_base.ReleaseTrack.ALPHA).resources
    self.new_versions = [
        self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-1')
    ]
    self.other_new_versions = [
        self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-2'),
        self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-3')
    ]
    self.identical_new_versions = [
        self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-2'),
        self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-2')
    ]
    self.igm_with_versions = self.messages.InstanceGroupManager(
        versions=[
            self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-1'),
            self.messages.InstanceGroupManagerVersion(instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-2')
        ]
    )
    self.igm_with_instance_template = self.messages.InstanceGroupManager(
        instanceTemplate='https://www.googleapis.com/compute/alpha/projects/fake-project/global/instanceTemplates/t-1'
    )

  def testAddAutoscalersToMigs(self):
    holder = base_classes.ComputeApiHolder(calliope_base.ReleaseTrack.GA)
    region = ('https://compute.googleapis.com/compute/v1/projects/{}/regions/'
              'us-central1').format(self.Project())
    migs = [{'region': region, 'name': 'my-mig'}]
    mig_url = ('https://compute.googleapis.com/compute/v1/projects/{}/'
               'regions/us-central1/instanceGroupManagers/my-mig').format(
                   self.Project())
    autoscaler = self.messages.Autoscaler(region=region, target=mig_url)

    self.StartObjectPatch(
        managed_instance_groups_utils, 'AutoscalersForLocations',
        return_value=[autoscaler])

    list(managed_instance_groups_utils.AddAutoscalersToMigs(iter(migs),
                                                            holder.client,
                                                            holder.resources))

    self.assertEqual(migs[0]['autoscaler'], autoscaler)

  def testAddAutoscalersToMigs_MismatchedRegionProjects(self):
    holder = base_classes.ComputeApiHolder(calliope_base.ReleaseTrack.GA)
    region = ('https://compute.googleapis.com/compute/v1/projects/{}/regions/'
              'us-central1').format(self.Project())
    migs = [{'region': region, 'name': 'my-mig'}]
    mig_url = ('https://compute.googleapis.com/compute/v1/projects/{}/'
               'regions/us-central1/instanceGroupManagers/my-mig').format(
                   self.Project())
    autoscaler = self.messages.Autoscaler(
        region=('https://compute.googleapis.com/compute/v1/projects/other-project/'
                'regions/us-central1'),
        target=mig_url)

    self.StartObjectPatch(
        managed_instance_groups_utils, 'AutoscalersForLocations',
        return_value=[autoscaler])

    list(managed_instance_groups_utils.AddAutoscalersToMigs(iter(migs),
                                                            holder.client,
                                                            holder.resources))

    self.assertEqual(migs[0]['autoscaler'], autoscaler)

  def testAllowedUtilizationTargetTypesMatchApi(self):
    self.assertEqual(
        managed_instance_groups_utils._ALLOWED_UTILIZATION_TARGET_TYPES,
        sorted(self.messages.AutoscalingPolicyCustomMetricUtilization
               .UtilizationTargetTypeValueValuesEnum.to_dict().keys()))

  def testValidateVersionsWithIgmVersions(self):
    managed_instance_groups_utils.ValidateVersions(
        self.igm_with_versions, self.new_versions, self.resources)

  def testValidateVersionsWithIgmInstanceTemplate(self):
    managed_instance_groups_utils.ValidateVersions(
        self.igm_with_instance_template, self.new_versions, self.resources)

  def testValidateVersionsWithIgmEmptyFail(self):
    with self.AssertRaisesToolExceptionMatches(
        'Either versions or instance template must be specified for '
        'managed instance group.'):
      managed_instance_groups_utils.ValidateVersions(
          self.messages.InstanceGroupManager(), self.new_versions, self.resources)

  def testValidateVersionsIdenticalFail(self):
    with self.AssertRaisesToolExceptionMatches(
        'Provided instance templates must be different.'):
      managed_instance_groups_utils.ValidateVersions(
          self.igm_with_versions, self.identical_new_versions, self.resources)

  def testValidateVersionsWithTooManyVersionsForce(self):
    managed_instance_groups_utils.ValidateVersions(
        self.igm_with_versions, self.other_new_versions, self.resources, force=True)

  def testValidateVersionsWithTooManyVersionsFail(self):
    with self.AssertRaisesToolExceptionMatches(
        'Update inconsistent with current state. '
        'The only allowed transitions between versions are: '
        'X -> Y, X -> (X, Y), (X, Y) -> X, (X, Y) -> Y, (X, Y) -> (X, Y). '
        'Please check versions templates or use --force.'):
      managed_instance_groups_utils.ValidateVersions(
          self.igm_with_versions, self.other_new_versions, self.resources)

  def testValidateVersionsWithTooManyVersionsAndInstanceTemplateForce(self):
    managed_instance_groups_utils.ValidateVersions(
        self.igm_with_instance_template, self.other_new_versions, self.resources, force=True)

  def testValidateVersionsWithTooManyVersionsAndInstanceTemplateFail(self):
    with self.AssertRaisesToolExceptionMatches(
        'Update inconsistent with current state. '
        'The only allowed transitions between versions are: '
        'X -> Y, X -> (X, Y), (X, Y) -> X, (X, Y) -> Y, (X, Y) -> (X, Y). '
        'Please check versions templates or use --force.'):
      managed_instance_groups_utils.ValidateVersions(
          self.igm_with_instance_template, self.other_new_versions, self.resources)


if __name__ == '__main__':
  test_case.main()
