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

"""Test of the 'clusters describe' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.calliope.concepts import handlers
from googlecloudsdk.core import properties
from tests.lib import sdk_test_base
from tests.lib.surface.dataproc import base
from tests.lib.surface.dataproc import unit_base


class ClustersDescribeUnitTest(unit_base.DataprocUnitTestBase):
  """Tests for dataproc clusters describe."""

  def testDescribeCluster(self):
    expected = self.MakeRunningCluster()
    self.ExpectGetCluster(expected)
    result = self.RunDataproc('clusters describe ' + self.CLUSTER_NAME)
    self.AssertMessagesEqual(expected, result)

  def testDescribeClusterNotFound(self):
    self.ExpectGetCluster(exception=self.MakeHttpError(404))
    message = 'Resource not found API reason: Resource not found.'
    with self.AssertRaisesHttpExceptionMatches(message):
      self.RunDataproc('clusters describe ' + self.CLUSTER_NAME)

  def testDescribeClusterRegionProperty(self):
    properties.VALUES.dataproc.region.Set('us-central1')
    expected = self.MakeRunningCluster()
    self.ExpectGetCluster(expected, region='us-central1')
    result = self.RunDataproc('clusters describe ' + self.CLUSTER_NAME)
    self.AssertMessagesEqual(expected, result)

  def testDescribeClusterRegionFlag(self):
    properties.VALUES.dataproc.region.Set('us-central1')
    expected = self.MakeRunningCluster()
    self.ExpectGetCluster(expected, region='us-east1')
    result = self.RunDataproc('clusters describe ' + self.CLUSTER_NAME +
                              ' --region us-east1')
    self.AssertMessagesEqual(expected, result)

  def testDescribeClusterNoRegionFlag(self):
    regex = r'Failed to find attribute \[region\]'
    with self.assertRaisesRegex(handlers.ParseError, regex):
      self.RunDataproc(
          'clusters describe ' + self.CLUSTER_NAME, set_region=False)


class ClustersDescribeUnitTestBeta(ClustersDescribeUnitTest,
                                   base.DataprocTestBaseBeta):
  """Tests for dataproc clusters describe."""

  def testBeta(self):
    self.assertEqual(self.messages, self._beta_messages)
    self.assertEqual(self.track, calliope_base.ReleaseTrack.BETA)


class ClustersDescribeUnitTestAlpha(ClustersDescribeUnitTestBeta,
                                    base.DataprocTestBaseAlpha):
  pass


if __name__ == '__main__':
  sdk_test_base.main()
