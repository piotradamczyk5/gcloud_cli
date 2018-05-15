# Copyright 2018 Google Inc. All Rights Reserved.
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
"""Tests for the sole-tenancy node-templates delete subcommand."""
from __future__ import absolute_import
from __future__ import unicode_literals
from apitools.base.py import encoding
from googlecloudsdk.calliope import base
from tests.lib import parameterized
from tests.lib import test_case
from tests.lib.surface.compute import test_base


class NodeTemplatesCreateTest(test_base.BaseTest, parameterized.TestCase):

  def SetUp(self):
    self.track = base.ReleaseTrack.ALPHA
    self.SelectApi(self.track.prefix)
    self.region = 'us-central1'

  def _ExpectCreate(self, template):
    request = self.messages.ComputeNodeTemplatesInsertRequest(
        project=self.Project(),
        region=self.region,
        nodeTemplate=template)
    self.make_requests.side_effect = [[template]]
    return request

  def _CreateAffinityLabelsMessage(self, affinity_labels):
    return encoding.DictToAdditionalPropertyMessage(
        affinity_labels, self.messages.NodeTemplate.NodeAffinityLabelsValue,
        sort_items=True)

  def testCreate_AllOptionsWithNodeType(self):
    affinity_labels = {'environment': 'prod', 'grouping': 'frontend'}
    template = self.messages.NodeTemplate(
        description='Awesome Template',
        name='my-template',
        nodeAffinityLabels=self._CreateAffinityLabelsMessage(affinity_labels),
        nodeType='n1-node-96-624')
    request = self._ExpectCreate(template)

    result = self.Run(
        'compute sole-tenancy node-templates create my-template '
        '--node-affinity-labels environment=prod,grouping=frontend '
        '--node-type n1-node-96-624 --description "Awesome Template" '
        '--region {}'.format(self.region))

    self.CheckRequests([(self.compute.nodeTemplates, 'Insert', request)])
    self.assertEqual(result, template)

  def testCreate_AllOptionsWithNodeRequirements(self):
    affinity_labels = {'environment': 'prod', 'grouping': 'frontend'}
    template = self.messages.NodeTemplate(
        description='Awesome Template',
        name='my-template',
        nodeAffinityLabels=self._CreateAffinityLabelsMessage(affinity_labels),
        nodeTypeFlexibility=self.messages.NodeTemplateNodeTypeFlexibility(
            cpus='64', localSsd='512', memory='any'))
    request = self._ExpectCreate(template)

    result = self.Run(
        'compute sole-tenancy node-templates create my-template '
        '--node-affinity-labels environment=prod,grouping=frontend '
        '--node-requirements vCPU=64,localSSD=512GB,memory=any '
        '--description "Awesome Template" --region {}'.format(self.region))

    self.CheckRequests([(self.compute.nodeTemplates, 'Insert', request)])
    self.assertEqual(result, template)

  @parameterized.named_parameters(
      ('OmittingMemoryRequirement', 'vCPU=64,localSSD=512GB', '64', '512',
       'any'),
      ('UnitConversion', 'localSSD=1TB,memory=16GB', 'any', '1024',
       '16384'),
      ('SettingCPUToAny', 'vCPU=any,localSSD=1TB,memory=16GB', 'any', '1024',
       '16384'),
      ('SettingAllToAny', 'vCPU=any,localSSD=any,memory=any', 'any', 'any',
       'any'),
      ('SettingAnyCaseInsensitive', 'vCPU=ANY,localSSD=Any,memory=anY',
       'any', 'any', 'any'),
      ('SettingAllToAnyMinimalKeys', 'localSSD=any', 'any', 'any', 'any'))
  def testCreate_NodeRequirements(self, node_requirements, cpus, local_ssd,
                                  memory):
    affinity_labels = {'environment': 'prod', 'grouping': 'frontend'}
    template = self.messages.NodeTemplate(
        name='my-template',
        nodeAffinityLabels=self._CreateAffinityLabelsMessage(affinity_labels),
        nodeTypeFlexibility=self.messages.NodeTemplateNodeTypeFlexibility(
            cpus=cpus, localSsd=local_ssd, memory=memory))
    request = self._ExpectCreate(template)

    result = self.Run(
        'compute sole-tenancy node-templates create my-template '
        '--node-affinity-labels environment=prod,grouping=frontend '
        '--node-requirements {0} '
        '--region {1}'.format(node_requirements, self.region))

    self.CheckRequests([(self.compute.nodeTemplates, 'Insert', request)])
    self.assertEqual(result, template)

  @parameterized.parameters(
      ('vCPU=whatever', "invalid .* value: 'vCPU=whatever'"),
      ('vCPU=whatever,memory=asdf',
       "invalid .* value: 'vCPU=whatever,memory=asdf'"),
      ('memory=51mg', 'unit must be one of .* received: mg'))
  def testCreate_InvalidNodeRequirements(self, node_requirements, error_msg):
    with self.AssertRaisesArgumentErrorRegexp(
        'argument --node-requirements: ' + error_msg):
      self.Run(
          'compute sole-tenancy node-templates create my-template '
          '--node-affinity-labels environment=prod,grouping=frontend '
          '--node-requirements {0} '
          '--region {1}'.format(node_requirements, self.region))

  def testCreate_NodeRequirementsMutuallyExlusiveWithNodeType(self):
    with self.AssertRaisesArgumentError():
      self.Run(
          'compute sole-tenancy node-templates create my-template '
          '--node-affinity-labels environment=prod,grouping=frontend '
          '--node-requirements localSSD=1TB,memory=16GB --node-type iAPX-286 '
          '--region {}'.format(self.region))
    self.AssertErrContains('--node-requirements')
    self.AssertErrContains('--node-type')


if __name__ == '__main__':
  test_case.main()