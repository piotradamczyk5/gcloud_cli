# -*- coding: utf-8 -*- #
# Copyright 2018 Google LLC. All Rights Reserved.
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
"""Tests that exercise workerpool deletion."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding
from apitools.base.py.testing import mock
from googlecloudsdk.api_lib.cloudbuild import cloudbuild_util
from googlecloudsdk.api_lib.util import apis as core_apis
from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.core import properties
from tests.lib import e2e_base
from tests.lib import sdk_test_base
from tests.lib import test_case


# TODO(b/29358031): Move WithMockHttp somewhere more appropriate for unit tests.
class DeleteTestBeta(e2e_base.WithMockHttp, sdk_test_base.WithFakeAuth):

  # Override only this method in subsequent classes for other release tracks.
  def PreSetUp(self):
    self.release_track = calliope_base.ReleaseTrack.BETA

  def SetUp(self):
    self.api_version = cloudbuild_util.RELEASE_TRACK_TO_API_VERSION[
        self.release_track]
    self.StartPatch('time.sleep')  # To speed up tests with polling
    self.mocked_cloudbuild_client = mock.Client(
        core_apis.GetClientClass('cloudbuild', self.api_version))
    self.mocked_cloudbuild_client.Mock()
    self.addCleanup(self.mocked_cloudbuild_client.Unmock)
    self.msg = core_apis.GetMessagesModule('cloudbuild', self.api_version)

    self.project_id = 'my-project'
    self.workerpool_location = cloudbuild_util.SERVICE_REGIONS[0]
    properties.VALUES.core.project.Set(self.project_id)

    self.frozen_time_str = '2018-11-12T00:10:00+00:00'

  def _Run(self, args):
    if self.release_track.prefix:
      self.Run([self.release_track.prefix] + args)
    else:
      self.Run(args)

  def testDelete(self):
    wp_in = self.msg.WorkerPool()
    wp_in.workerConfig = self.msg.WorkerConfig()
    wp_in.name = 'fake_name'

    self.mocked_cloudbuild_client.projects_locations_workerPools.Delete.Expect(
        self.msg.CloudbuildProjectsLocationsWorkerPoolsDeleteRequest(
            name='projects/{}/locations/{}/workerPools/{}'.format(
                self.project_id, self.workerpool_location, wp_in.name)),
        response=self.msg.Operation(
            response=encoding.JsonToMessage(
                self.msg.Operation.ResponseValue,
                encoding.MessageToJson(self.msg.Empty()))))

    self._Run([
        'builds', 'worker-pools', 'delete', wp_in.name, '--region',
        self.workerpool_location
    ])


class DeleteTestAlpha(DeleteTestBeta):

  def PreSetUp(self):
    self.release_track = calliope_base.ReleaseTrack.ALPHA

  def testDelete(self):
    wp_in = self.msg.WorkerPool()
    wp_in.workerConfig = self.msg.WorkerConfig()
    wp_in.name = 'fake_name'

    self.mocked_cloudbuild_client.projects_workerPools.Delete.Expect(
        self.msg.CloudbuildProjectsWorkerPoolsDeleteRequest(
            name='projects/{}/workerPools/{}'.format(self.project_id,
                                                     wp_in.name)),
        response=self.msg.Empty())

    self._Run(['builds', 'worker-pools', 'delete', wp_in.name])


if __name__ == '__main__':
  test_case.main()
