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
"""Tests for creating Server CA Certs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from apitools.base.protorpclite import util as protorpc_util

from tests.lib import test_case
from tests.lib.surface.sql import base
from tests.lib.surface.sql import data


class _BaseServerCaCertsCreateTest(object):

  def testCreateCert(self):
    instance_name = 'integration-test'

    self.mocked_client.instances.AddServerCa.Expect(
        self.messages.SqlInstancesAddServerCaRequest(
            instance=instance_name,
            project=self.Project(),
        ),
        data.GetOperation(
            self.Project(),
            self.messages.DatabaseInstance(
                kind='sql#instance', name=instance_name),
            self.messages.Operation.OperationTypeValueValuesEnum.UPDATE,
            self.messages.Operation.StatusValueValuesEnum.PENDING))
    self.mocked_client.operations.Get.Expect(
        data.GetOperationGetRequest(self.Project()),
        data.GetOperation(
            self.Project(),
            self.messages.DatabaseInstance(
                kind='sql#instance', name=instance_name),
            self.messages.Operation.OperationTypeValueValuesEnum.UPDATE,
            self.messages.Operation.StatusValueValuesEnum.DONE))

    # The upcoming cert has fingerprint 'three'.
    active_cert_fingerprint = 'two'

    # The list endpoint is called to check the newly created cert.
    self.mocked_client.instances.ListServerCas.Expect(
        self.messages.SqlInstancesListServerCasRequest(
            instance=instance_name,
            project=self.Project(),
        ),
        self.messages.InstancesListServerCasResponse(
            activeVersion=active_cert_fingerprint,
            certs=[
                data.GetSslCert(
                    instance_name, 'one',
                    datetime.datetime(
                        2024,
                        2,
                        2,
                        21,
                        10,
                        29,
                        402000,
                        tzinfo=protorpc_util.TimeZoneOffset(
                            datetime.timedelta(0))).isoformat()),
                data.GetSslCert(
                    instance_name, 'two',
                    datetime.datetime(
                        2024,
                        4,
                        4,
                        21,
                        10,
                        29,
                        402000,
                        tzinfo=protorpc_util.TimeZoneOffset(
                            datetime.timedelta(0))).isoformat()),
                data.GetSslCert(
                    instance_name, 'three',
                    datetime.datetime(
                        2024,
                        5,
                        5,
                        21,
                        10,
                        29,
                        402000,
                        tzinfo=protorpc_util.TimeZoneOffset(
                            datetime.timedelta(0))).isoformat())
            ],
            kind='sql#sslCertsList',
        ))
    self.Run(
        'sql ssl server-ca-certs create --instance={}'.format(instance_name))
    self.AssertOutputContains(
        """\
SHA1_FINGERPRINT EXPIRATION
three            2024-05-05T21:10:29.402000+00:00
""",
        normalize_space=True)


class ServerCaCertsCreateBetaTest(_BaseServerCaCertsCreateTest,
                                  base.SqlMockTestBeta):
  pass


class ServerCaCertsCreateAlphaTest(_BaseServerCaCertsCreateTest,
                                   base.SqlMockTestAlpha):
  pass


if __name__ == '__main__':
  test_case.main()
