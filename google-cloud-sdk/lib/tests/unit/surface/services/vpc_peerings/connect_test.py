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
"""Unit tests for service-management enable command."""

from __future__ import absolute_import
from __future__ import unicode_literals
from googlecloudsdk.api_lib.cloudresourcemanager import projects_api
from googlecloudsdk.api_lib.services import exceptions
from tests.lib import test_case
from tests.lib.apitools import http_error
from tests.lib.surface.services import unit_test_base


class ConnectTest(unit_test_base.SNV1alphaUnitTestBase):
  """Unit tests for services vpc-peerings connect command."""
  OPERATION_NAME = 'operations/abc.0000000000'
  NETWORK = 'hello'
  RANGES = ['10.0.1.0/30', '10.0.3.0/30']

  def testConnect(self):
    self.ExpectPeerApiCall(self.NETWORK, self.RANGES, self.OPERATION_NAME)
    self.ExpectOperation(self.OPERATION_NAME, 3)
    self.SetProjectNumber()

    self.Run('alpha services vpc-peerings connect --service=%s --network=%s '
             '--reserved-ranges=%s' % (self.DEFAULT_SERVICE_NAME, self.NETWORK,
                                       ','.join(self.RANGES)))
    self.AssertErrContains(self.OPERATION_NAME)
    self.AssertErrContains('finished successfully')

  def testConnectAsync(self):
    self.ExpectPeerApiCall(self.NETWORK, self.RANGES, self.OPERATION_NAME)
    self.SetProjectNumber()

    self.Run('alpha services vpc-peerings connect --service=%s --network=%s '
             '--reserved-ranges=%s --async' %
             (self.DEFAULT_SERVICE_NAME, self.NETWORK, ','.join(self.RANGES)))
    self.AssertErrContains(self.OPERATION_NAME)
    self.AssertErrContains('operation is in progress')

  def testConnectPermissionDenied(self):
    server_error = http_error.MakeDetailedHttpError(code=403, message='Error.')
    self.ExpectPeerApiCall(self.NETWORK, self.RANGES, None, error=server_error)
    self.SetProjectNumber()

    with self.assertRaisesRegex(
        exceptions.PeerServicePermissionDeniedException, r'Error.'):
      self.Run('alpha services vpc-peerings connect --service=%s --network=%s '
               '--reserved-ranges=%s' % (self.DEFAULT_SERVICE_NAME,
                                         self.NETWORK, ','.join(self.RANGES)))

  def SetProjectNumber(self):
    mock_get = self.StartObjectPatch(projects_api, 'Get')
    p = Project()
    p.SetProjectNumber(self.PROJECT_NUMBER)
    mock_get.return_value = p


class Project(object):

  # pylint: disable=invalid-name
  def SetProjectNumber(self, num):
    self.projectNumber = num


if __name__ == '__main__':
  test_case.main()