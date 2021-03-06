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
"""Tests that exercise operations listing and executing."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from apitools.base.protorpclite import util as protorpc_util

from googlecloudsdk.core.console import console_io
from tests.lib import test_case
from tests.lib.surface.sql import base


class _BaseInstancesResetSSLConfigTest(object):
  # pylint:disable=g-tzinfo-datetime

  def _ExpectResetSSLConfig(self):
    self.mocked_client.instances.ResetSslConfig.Expect(
        self.messages.SqlInstancesResetSslConfigRequest(
            instance='reset-test',
            project=self.Project(),
        ),
        self.messages.Operation(
            # pylint:disable=line-too-long
            insertTime=datetime.datetime(
                2014,
                8,
                12,
                19,
                38,
                39,
                415000,
                tzinfo=protorpc_util.TimeZoneOffset(
                    datetime.timedelta(0))).isoformat(),
            startTime=datetime.datetime(
                2014,
                8,
                12,
                19,
                38,
                39,
                525000,
                tzinfo=protorpc_util.TimeZoneOffset(
                    datetime.timedelta(0))).isoformat(),
            endTime=datetime.datetime(
                2014,
                8,
                12,
                19,
                39,
                26,
                601000,
                tzinfo=protorpc_util.TimeZoneOffset(
                    datetime.timedelta(0))).isoformat(),
            error=None,
            exportContext=None,
            importContext=None,
            targetId='reset-test',
            targetLink='https://sqladmin.googleapis.com/sql/v1beta4/projects/{0}/instances/patch-instance3'
            .format(self.Project()),
            targetProject=self.Project(),
            kind='sql#operation',
            name='4d5a6c5e-38fc-4ac5-9980-72ee44c621d8',
            selfLink='https://sqladmin.googleapis.com/sql/v1beta4/projects/{0}/operations/4d5a6c5e-38fc-4ac5-9980-72ee44c621d8'
            .format(self.Project()),
            operationType=self.messages.Operation.OperationTypeValueValuesEnum
            .UPDATE,
            status=self.messages.Operation.StatusValueValuesEnum.DONE,
            user='170350250316@developer.gserviceaccount.com',
        ))

    self.mocked_client.operations.Get.Expect(
        self.messages.SqlOperationsGetRequest(
            operation='4d5a6c5e-38fc-4ac5-9980-72ee44c621d8',
            project=self.Project(),
        ),
        self.messages.Operation(
            # pylint:disable=line-too-long
            insertTime=datetime.datetime(
                2014,
                8,
                12,
                19,
                38,
                39,
                415000,
                tzinfo=protorpc_util.TimeZoneOffset(
                    datetime.timedelta(0))).isoformat(),
            startTime=datetime.datetime(
                2014,
                8,
                12,
                19,
                38,
                39,
                525000,
                tzinfo=protorpc_util.TimeZoneOffset(
                    datetime.timedelta(0))).isoformat(),
            endTime=datetime.datetime(
                2014,
                8,
                12,
                19,
                39,
                26,
                601000,
                tzinfo=protorpc_util.TimeZoneOffset(
                    datetime.timedelta(0))).isoformat(),
            error=None,
            exportContext=None,
            importContext=None,
            targetId='reset-test',
            targetLink='https://sqladmin.googleapis.com/sql/v1beta4/projects/{0}/instances/patch-instance3'
            .format(self.Project()),
            targetProject=self.Project(),
            kind='sql#operation',
            name='4d5a6c5e-38fc-4ac5-9980-72ee44c621d8',
            selfLink='https://sqladmin.googleapis.com/sql/v1beta4/projects/{0}/operations/4d5a6c5e-38fc-4ac5-9980-72ee44c621d8'
            .format(self.Project()),
            operationType=self.messages.Operation.OperationTypeValueValuesEnum
            .UPDATE,
            status=self.messages.Operation.StatusValueValuesEnum.DONE,
            user='170350250316@developer.gserviceaccount.com',
        ))

  def testSimpleReset(self):
    self._ExpectResetSSLConfig()

    self.Run('sql instances reset-ssl-config reset-test')
    self.AssertErrContains(
        'Reset SSL config for [https://sqladmin.googleapis.com/sql/v1beta4/'
        'projects/{0}/instances/reset-test].'.format(self.Project()))

  def testResetAsync(self):
    self._ExpectResetSSLConfig()

    self.Run('sql instances reset-ssl-config reset-test --async')
    self.AssertErrNotContains(
        'Reset SSL config for [https://sqladmin.googleapis.com/sql/v1beta4/'
        'projects/{0}/instances/reset-test].'.format(self.Project()))

  def testResetNoConfirmCancels(self):
    self.WriteInput('n\n')
    with self.assertRaises(console_io.OperationCancelledError):
      self.Run('sql instances reset-ssl-config reset-test')


class InstancesResetSSLConfigGATest(_BaseInstancesResetSSLConfigTest,
                                    base.SqlMockTestGA):
  pass


class InstancesResetSSLConfigBetaTest(_BaseInstancesResetSSLConfigTest,
                                      base.SqlMockTestBeta):
  pass


class InstancesResetSSLConfigAlphaTest(_BaseInstancesResetSSLConfigTest,
                                       base.SqlMockTestAlpha):
  pass


if __name__ == '__main__':
  test_case.main()
