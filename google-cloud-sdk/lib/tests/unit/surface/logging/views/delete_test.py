# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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

"""Tests of the 'views delete' subcommand."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from tests.lib import test_case
from tests.lib.apitools import http_error
from tests.lib.surface.logging import base


class ViewsDeleteTest(base.LoggingTestBase):

  def testDelete(self):
    self.mock_client_v2.projects_locations_buckets_views.Delete.Expect(
        self.msgs.LoggingProjectsLocationsBucketsViewsDeleteRequest(
            name='projects/my-project/locations/global/buckets/my-bucket'
                 '/views/my-view'),
        self.msgs.Empty())
    self.RunLogging(
        'views delete my-view --location=global --bucket=my-bucket',
        calliope_base.ReleaseTrack.ALPHA)
    self.AssertErrContains('Deleted')

  def testDeleteOrganization(self):
    self.mock_client_v2.projects_locations_buckets_views.Delete.Expect(
        self.msgs.LoggingProjectsLocationsBucketsViewsDeleteRequest(
            name='organizations/1234/locations/global/buckets/my-bucket'
                 '/views/my-view'),
        self.msgs.Empty())
    self.RunLogging(
        'views delete my-view --bucket=my-bucket --location=global '
        '--organization=1234',
        calliope_base.ReleaseTrack.ALPHA)
    self.AssertErrContains('Deleted')

  def testDeleteNoPerms(self):
    self.mock_client_v2.projects_locations_buckets_views.Delete.Expect(
        self.msgs.LoggingProjectsLocationsBucketsViewsDeleteRequest(
            name='projects/my-project/locations/global/buckets/my-bucket'
                 '/views/my-view'),
        exception=http_error.MakeHttpError(403))
    self.RunWithoutPerms('views delete my-view --bucket=my-bucket '
                         '--location=global -q',
                         calliope_base.ReleaseTrack.ALPHA)

  def testDeleteNoProject(self):
    self.RunWithoutProject('views delete my-view --bucket=my-bucket '
                           '--location=global',
                           calliope_base.ReleaseTrack.ALPHA)

  def testDeleteNoAuth(self):
    self.RunWithoutAuth('views delete my-view --bucket=my-bucket '
                        '--location=global',
                        calliope_base.ReleaseTrack.ALPHA)


if __name__ == '__main__':
  test_case.main()
