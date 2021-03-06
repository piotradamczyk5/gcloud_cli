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
"""Tests for the instance-groups list-instances subcommand."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.util import apis as core_apis
from tests.lib import cli_test_base
from tests.lib import sdk_test_base
from tests.lib import test_case
from tests.lib.surface.compute import test_base
from tests.lib.surface.compute.instance_groups import test_resources
import mock


class InstanceGroupsListInstancesTest(test_base.BaseTest):

  def SetUp(self):
    self.SelectApi('v1')
    self.make_requests.side_effect = iter([
        test_resources.MakeInstancesInInstanceGroup(
            self.messages, self.resource_api),
    ])

  def testListInstances(self):
    self.Run("""
        compute instance-groups list-instances group-1
          --zone central2-a
        """)
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            inst-3 central2-a STOPPED
            """), normalize_space=True)

  def testListInstancesWithLimit(self):
    self.Run("""
        compute instance-groups list-instances group-1
          --zone central2-a
          --limit 2
        """)
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            """), normalize_space=True)

  def testListInstancesByUri(self):
    self.Run("""
        compute instance-groups list-instances
          {0}/projects/my-project/zones/central2-a/instanceGroups/group-1
          --zone central2-a
        """.format(self.compute_uri))
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            inst-3 central2-a STOPPED
            """), normalize_space=True)

  def testListInstancesWithFilter(self):
    self.Run("""
        compute instance-groups list-instances
          {0}/projects/my-project/zones/central2-a/instanceGroups/group-1
          --zone central2-a
          --regexp ".*inst.*"
        """.format(self.compute_uri))
    self.CheckRequests(
        [(self.compute.instanceGroups,
          'ListInstances',
          self.messages.ComputeInstanceGroupsListInstancesRequest(
              filter='instance eq .*inst.*',
              instanceGroup='group-1',
              instanceGroupsListInstancesRequest=(
                  self.messages.InstanceGroupsListInstancesRequest()),
              project='my-project',
              zone='central2-a'))])
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            inst-3 central2-a STOPPED
            """), normalize_space=True)

  def testListInstancesBySorted(self):
    self.Run("""
        compute instance-groups list-instances group-1
          --zone central2-a
          --sort-by ~NAME
        """)
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-3 central2-a STOPPED
            inst-2 central2-a RUNNING
            inst-1 central2-a RUNNING
            """), normalize_space=True)

  def testListInstancesUriOutput(self):
    self.Run("""
        compute instance-groups list-instances group-1
          --zone central2-a
          --uri
        """)
    self.AssertOutputEquals(
        textwrap.dedent("""\
            {0}/projects/my-project/zones/central2-a/instances/inst-1
            {0}/projects/my-project/zones/central2-a/instances/inst-2
            {0}/projects/my-project/zones/central2-a/instances/inst-3
            """.format(self.compute_uri)))

  def testListInstancesZone(self):
    self.Run("""
        compute instance-groups list-instances group-1
          --zone central2-a
        """)
    self.CheckRequests(
        [(self.compute.instanceGroups,
          'ListInstances',
          self.messages.ComputeInstanceGroupsListInstancesRequest(
              instanceGroup='group-1',
              instanceGroupsListInstancesRequest=(
                  self.messages.InstanceGroupsListInstancesRequest()),
              zone='central2-a',
              project='my-project'))],
    )
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            inst-3 central2-a STOPPED
            """), normalize_space=True)

  def testListInstancesRegion(self):
    self.Run("""
        compute instance-groups list-instances group-1
          --region central2
        """)
    self.CheckRequests(
        [(self.compute.regionInstanceGroups,
          'ListInstances',
          self.messages.ComputeRegionInstanceGroupsListInstancesRequest(
              instanceGroup='group-1',
              regionInstanceGroupsListInstancesRequest=(
                  self.messages.RegionInstanceGroupsListInstancesRequest()),
              region='central2',
              project='my-project'))],
    )
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            inst-3 central2-a STOPPED
            """), normalize_space=True)

  def testListInstancesPromptScope(self):
    self.StartPatch('googlecloudsdk.core.console.console_io.CanPrompt',
                    return_value=True)
    self.make_requests.side_effect = iter([
        [self.messages.Region(name='central2')],
        [self.messages.Zone(name='central2-a'),
         self.messages.Zone(name='central2-b')],
        test_resources.MakeInstancesInInstanceGroup(
            self.messages, 'v1'),
    ])
    self.WriteInput('1\n')
    self.Run("""
        compute instance-groups list-instances group-1
        """)
    self.CheckRequests(
        self.regions_list_request,
        self.zones_list_request,
        [(self.compute.regionInstanceGroups,
          'ListInstances',
          self.messages.ComputeRegionInstanceGroupsListInstancesRequest(
              instanceGroup='group-1',
              regionInstanceGroupsListInstancesRequest=(
                  self.messages.RegionInstanceGroupsListInstancesRequest()),
              region='central2',
              project='my-project'))],
    )
    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS
            inst-1 central2-a RUNNING
            inst-2 central2-a RUNNING
            inst-3 central2-a STOPPED
            """), normalize_space=True)


class InstanceGroupsListInstancesPaginationTest(
    sdk_test_base.WithFakeAuth, cli_test_base.CliTestBase):

  API_VERSION = 'v1'

  def SetUp(self):
    self.messages = core_apis.GetMessagesModule('compute', self.API_VERSION)
    batch_make_requests_patcher = mock.patch(
        'googlecloudsdk.api_lib.compute.batch_helper.MakeRequests',
        autospec=True)
    self.addCleanup(batch_make_requests_patcher.stop)
    self.batch_make_requests = batch_make_requests_patcher.start()

  def testListInstancesWithPagination(self):
    items = test_resources.MakeInstancesInManagedInstanceGroup(
        self.messages, self.API_VERSION)

    self.batch_make_requests.side_effect = iter([
        [[self.messages.InstanceGroupManagersListManagedInstancesResponse(
            managedInstances=[items[0], items[1]], nextPageToken='token-1')],
         []],
        [[self.messages.InstanceGroupManagersListManagedInstancesResponse(
            managedInstances=[items[2], items[3]],)],
         []]
    ])

    self.Run("""
        compute instance-groups managed list-instances group-1
          --zone central2-a
        """)

    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS  HEALTH_STATE ACTION      INSTANCE_TEMPLATE VERSION_NAME LAST_ERROR
            inst-1 central2-a RUNNING HEALTHY      NONE        template-1        xxx
            inst-2 central2-a STOPPED UNHEALTHY    RECREATING  template-1
            inst-3 central2-a RUNNING TIMEOUT      DELETING    template-2        yyy
            inst-4 central2-a                      CREATING    template-3                     Error CONDITION_NOT_MET: True is not False, Error QUOTA_EXCEEDED: Limit is 5
            """),
        normalize_space=True)

  def testListInstancesWithoutPagination(self):
    items = test_resources.MakeInstancesInManagedInstanceGroup(
        self.messages, self.API_VERSION)

    self.batch_make_requests.side_effect = iter([
        [[self.messages.InstanceGroupManagersListManagedInstancesResponse(
            managedInstances=[items[0], items[1]],)],
         []],
        [[self.messages.InstanceGroupManagersListManagedInstancesResponse(
            managedInstances=[items[2], items[3]],)],
         []]
    ])

    self.Run("""
        compute instance-groups managed list-instances group-1
          --zone central2-a
        """)

    self.AssertOutputEquals(
        textwrap.dedent("""\
            NAME   ZONE       STATUS  HEALTH_STATE ACTION      INSTANCE_TEMPLATE VERSION_NAME LAST_ERROR
            inst-1 central2-a RUNNING HEALTHY      NONE        template-1        xxx
            inst-2 central2-a STOPPED UNHEALTHY    RECREATING  template-1
            """),
        normalize_space=True)

if __name__ == '__main__':
  test_case.main()
