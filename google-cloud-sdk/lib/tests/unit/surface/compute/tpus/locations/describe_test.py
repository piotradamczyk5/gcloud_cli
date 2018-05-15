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
"""tpus locations describe tests."""

from __future__ import absolute_import
from __future__ import unicode_literals
from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.core import properties
from tests.lib import parameterized
from tests.lib import test_case
from tests.lib.surface.compute.tpus import base


@parameterized.parameters([calliope_base.ReleaseTrack.ALPHA,
                           calliope_base.ReleaseTrack.BETA])
class DescribeTest(base.TpuUnitTestBase):

  def SetUp(self):
    self.zone = 'us-central1-c'
    properties.VALUES.compute.zone.Set(self.zone)

  def testDescribe(self, track):
    self._SetTrack(track)
    location = self.GetTestLocation(name='us-east-2')
    self.mock_client.projects_locations.Get.Expect(
        self.messages.TpuProjectsLocationsGetRequest(
            name='projects/{}/locations/us-east-2'.format(self.Project())),
        location)

    self.assertEqual(
        self.Run('compute tpus locations describe us-east-2'),
        location)


if __name__ == '__main__':
  test_case.main()