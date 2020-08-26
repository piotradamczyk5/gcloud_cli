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
#
"""Tests for the grpc_util module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.core import gapic_util
from tests.lib import sdk_test_base
from tests.lib import test_case


class GapicUtilTest(sdk_test_base.WithFakeAuth):

  def testGetStoredCredentials(self):
    credentials = gapic_util.StoredCredentials()
    self.assertEqual(self.FakeAuthAccessToken(), credentials.token)


if __name__ == '__main__':
  test_case.main()