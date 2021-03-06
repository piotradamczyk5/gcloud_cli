# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
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
"""Base class for all sql tests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py.testing import mock

from googlecloudsdk.api_lib.util import apis as core_apis
from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.core import metrics
from googlecloudsdk.core import properties
from tests.lib import e2e_base
from tests.lib import e2e_utils
from tests.lib import sdk_test_base
from tests.lib.surface.sql import mocks


class _SqlTestBase(object):
  """Base class for all SQL tests."""
  PROJECT_ID = 'testproject'
  INSTANCE_ID = 'testinstance'


class SqlIntegrationTestBase(e2e_base.WithServiceAuth, _SqlTestBase):
  """Base class for all SQL e2e tests."""

  def SetUp(self):
    metrics.StartTestMetrics('SQL', '{0}.{1}'.format(self.__class__.__name__,
                                                     self._testMethodName))

  def TearDown(self):
    metrics.StopTestMetrics()


class SqlIntegrationTestBaseWithNewInstance(SqlIntegrationTestBase):
  """Base class for all SQL e2e tests that need a fresh SQL instance."""

  @sdk_test_base.Retry(why=('Because sql backend service is flaky.'))
  def CreateInstance(self, tier):
    self.test_instance = next(
        e2e_utils.GetResourceNameGenerator(prefix='gcloud-sql-test'))
    self.instance_created = False
    operation = self.RunCreateInstanceCmd(tier)
    self.WaitOnOperation(operation.name)
    self.instance_created = True

  @sdk_test_base.Retry(why=('Because sql backend service is flaky.'))
  def DeleteInstance(self):
    self.Run('sql instances delete {0} --async'.format(self.test_instance))

  def WaitOnOperation(self, operation_id):
    self.Run('sql operations wait {0} --timeout=unlimited'.format(operation_id))

  def SetUp(self):
    properties.VALUES.core.disable_prompts.Set(True)

  def TearDown(self):
    if self.instance_created:
      self.DeleteInstance()


class MysqlIntegrationTestBase(SqlIntegrationTestBaseWithNewInstance):
  # Base class for all SQL e2e tests that need a fresh MySQL instance.

  def RunCreateInstanceCmd(self, tier):
    # TODO(b/73362371): Specify a region or zone.
    return self.Run(
        'sql instances create {0} --tier {1} --backup --enable-bin-log '
        '--backup-start-time 00:00 --async --quiet'.format(
            self.test_instance, tier))


class PsqlIntegrationTestBase(SqlIntegrationTestBaseWithNewInstance):
  # Base class for all SQL e2e tests that need a fresh PSQL instance.

  def RunCreateInstanceCmd(self, tier):
    # TODO(b/73362371): Specify a region or zone.
    return self.Run(
        'sql instances create {0} --database-version POSTGRES_9_6 '
        '--tier {1} --activation-policy ALWAYS --async --quiet'.format(
            self.test_instance, tier),
        track=calliope_base.ReleaseTrack.BETA)


class SqlMockTestBase(sdk_test_base.WithFakeAuth, e2e_base.WithMockHttp,
                      _SqlTestBase, mocks.MockEndpoints):
  """Base class for all SQL unit tests."""

  def SetUp(self):
    self.mocked_client = mock.Client(core_apis.GetClientClass('sql', 'v1beta4'))
    self.mocked_client.Mock()
    self.addCleanup(self.mocked_client.Unmock)

    self.messages = core_apis.GetMessagesModule('sql', 'v1beta4')

    # Stop sleeping for 1 second every time we wait for operation
    self.StartPatch('time.sleep')


class SqlMockTestGA(SqlMockTestBase):
  """Base class for all SQL GA unit tests."""
  pass


class SqlMockTestBeta(SqlMockTestBase):
  """Base class for all SQL BETA unit tests."""

  def Run(self, cmd, track=None):
    return super(SqlMockTestBeta, self).Run(
        cmd, track=calliope_base.ReleaseTrack.BETA)


class SqlMockTestAlpha(SqlMockTestBase):
  """Base class for all SQL ALPHA unit tests."""

  def Run(self, cmd, track=None):
    return super(SqlMockTestAlpha, self).Run(
        cmd, track=calliope_base.ReleaseTrack.ALPHA)
