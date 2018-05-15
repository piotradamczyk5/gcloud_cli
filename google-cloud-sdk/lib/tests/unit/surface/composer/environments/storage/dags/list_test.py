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
"""Unit tests for environments storage dags list."""

from __future__ import absolute_import
from __future__ import unicode_literals
from googlecloudsdk.core import properties
from tests.lib import test_case
from tests.lib.surface.composer import base
import six


class EnvironmentsStorageDagsListTest(base.StorageApiCallingUnitTest):

  def SetUp(self):
    # Disable user output to not exhaust the generator returned by
    # RunEnvironments
    properties.VALUES.core.user_output_enabled.Set(False)

  def testDagsList(self):
    """Tests successful DAG listing."""
    file_names = [
        'dags/', 'dags/file1.py', 'dags/file2.py', 'dags/folder',
        'dags/file3.py'
    ]
    response = self.storage_messages.Objects(
        items=[self.storage_messages.Object(name=name) for name in file_names])

    self.ExpectEnvironmentGet(
        self.TEST_PROJECT,
        self.TEST_LOCATION,
        self.TEST_ENVIRONMENT_ID,
        response=self.MakeEnvironmentWithBucket())

    self.ExpectObjectList(self.test_gcs_bucket, 'dags/', responses=[response])

    actual_responses = self.RunEnvironments(
        'storage', 'dags', 'list', '--project', self.TEST_PROJECT, '--location',
        self.TEST_LOCATION, '--environment', self.TEST_ENVIRONMENT_ID)
    six.assertCountEqual(self, response.items, actual_responses)


if __name__ == '__main__':
  test_case.main()