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

"""Tests of the 'locations' subcommand."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from tests.lib import test_case
from tests.lib.apitools import http_error
from tests.lib.surface.logging import base


class ProjectsLocationsGetTest(base.LoggingTestBase):

  def testGet(self):
    test_location = self.msgs.Location(locationId='my-location')
    self.mock_client_v2.projects_locations.Get.Expect(
        self.msgs.LoggingProjectsLocationsGetRequest(
            name='projects/my-project/locations/my-location'),
        test_location)
    self.RunLogging(
        'locations describe my-location', calliope_base.ReleaseTrack.ALPHA)
    self.AssertOutputContains(test_location.locationId)

  def testGetNoPerms(self):
    self.mock_client_v2.projects_locations.Get.Expect(
        self.msgs.LoggingProjectsLocationsGetRequest(
            name='projects/my-project/locations/my-location'),
        exception=http_error.MakeHttpError(403))
    self.RunWithoutPerms(
        'locations describe my-location', calliope_base.ReleaseTrack.ALPHA)

  def testGetNoProject(self):
    self.RunWithoutProject(
        'locations describe my-location', calliope_base.ReleaseTrack.ALPHA)

  def testGetNoAuth(self):
    self.RunWithoutAuth(
        'locations describe my-location', calliope_base.ReleaseTrack.ALPHA)


if __name__ == '__main__':
  test_case.main()
