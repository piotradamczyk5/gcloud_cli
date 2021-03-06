# -*- coding: utf-8 -*- #
# Copyright 2017 Google LLC. All Rights Reserved.
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
"""Test of the 'operations list' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.firestore import operations
from googlecloudsdk.calliope import base as calliope_base
from tests.lib import test_case
from tests.lib.surface.firestore import base


class ListTestGA(base.FirestoreCommandUnitTest):
  """Tests the GA firestore operations list command."""

  def PreSetUp(self):
    self.track = calliope_base.ReleaseTrack.GA

  def testList(self):
    request = self.GetMockListRequest()

    operation_name = 'export operation name'

    operation_list = [
        operations.GetMessages().GoogleLongrunningOperation(
            done=False, name=operation_name)
    ]

    response = operations.GetMessages().GoogleLongrunningListOperationsResponse(
        operations=operation_list)

    self.mock_firestore_v1.projects_databases_operations.List.Expect(
        request, response=response)

    actual = list(self.RunFirestoreTest('operations list'))
    self.assertEqual(1, len(actual))
    self.assertEqual(operation_name, actual[0].name)

  def testListWithCollectionIdsGetsTranslated(self):
    expected_filter = 'metadata.collectionIds=a,b'
    request = self.GetMockListRequest(operation_filter=expected_filter)

    operation_name = 'export operation name'

    operation_list = [
        operations.GetMessages().GoogleLongrunningOperation(
            done=False, name=operation_name)
    ]

    response = operations.GetMessages().GoogleLongrunningListOperationsResponse(
        operations=operation_list)

    self.mock_firestore_v1.projects_databases_operations.List.Expect(
        request, response=response)

    actual = list(
        self.RunFirestoreTest(
            'operations list --filter=\'collectionIds:a,b\''))
    self.assertEqual(1, len(actual))
    self.assertEqual(operation_name, actual[0].name)

  def GetMockListRequest(self,
                         operation_filter=None,
                         page_size=operations.DEFAULT_PAGE_SIZE,
                         page_token=None):
    return operations.GetMessages(
    ).FirestoreProjectsDatabasesOperationsListRequest(
        filter=operation_filter,
        name='projects/%s/databases/(default)' % (self.Project()),
        pageSize=page_size,
        pageToken=page_token)


class ListTestBeta(ListTestGA):
  """Tests the beta firestore operations list command."""

  def PreSetUp(self):
    self.track = calliope_base.ReleaseTrack.BETA


class ListTestAlpha(ListTestBeta):
  """Tests the alpha firestore operations list command."""

  def PreSetUp(self):
    self.track = calliope_base.ReleaseTrack.ALPHA


if __name__ == '__main__':
  test_case.main()
