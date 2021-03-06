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

"""Tests that ensure getting an IAM policy works properly."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.command_lib.iam import iam_util
from tests.lib import cli_test_base
from tests.lib import test_case
from tests.lib.surface.iam import unit_test_base


class GetIamPolicyTestGA(unit_test_base.BaseTest, test_case.WithOutputCapture):

  def SetUp(self):
    self.track = calliope_base.ReleaseTrack.GA

  def testGetIamPolicy(self):
    policy = self.msgs.Policy(
        version=1,
        bindings=[
            self.msgs.Binding(
                role='roles/owner',
                members=['user:test-user@gmail.com']),
            self.msgs.Binding(
                role='roles/viewer',
                members=['allUsers'])])

    self.client.projects_serviceAccounts.GetIamPolicy.Expect(
        request=self.msgs.IamProjectsServiceAccountsGetIamPolicyRequest(
            resource=('projects/-/serviceAccounts/'
                      'test@test-project.iam.gserviceaccount.com'),
            options_requestedPolicyVersion=
            iam_util.MAX_LIBRARY_IAM_SUPPORTED_VERSION),
        response=policy)

    result = self.Run('iam service-accounts get-iam-policy --format=disable '
                      'test@test-project.iam.gserviceaccount.com')

    self.assertEqual(result, policy)

  def testListCommandFilter(self):
    policy = self.msgs.Policy(
        version=1,
        bindings=[
            self.msgs.Binding(
                role='roles/owner',
                members=['user:test-user@gmail.com']),
            self.msgs.Binding(
                role='roles/viewer',
                members=['allUsers'])])

    self.client.projects_serviceAccounts.GetIamPolicy.Expect(
        request=self.msgs.IamProjectsServiceAccountsGetIamPolicyRequest(
            resource=('projects/-/serviceAccounts/'
                      'test@test-project.iam.gserviceaccount.com'),
            options_requestedPolicyVersion=
            iam_util.MAX_LIBRARY_IAM_SUPPORTED_VERSION),
        response=policy)

    self.Run("""
        iam service-accounts get-iam-policy
        test@test-project.iam.gserviceaccount.com
        --flatten=bindings[].members
        --filter=bindings.role:roles/owner
        --format=value(bindings.members)
        """)

    self.AssertOutputEquals('user:test-user@gmail.com\n')

  def testGetIamPolicyUsingServiceAccount(self):
    policy = self.msgs.Policy(
        version=1,
        bindings=[
            self.msgs.Binding(
                role='roles/owner',
                members=['user:test-user@gmail.com']),
            self.msgs.Binding(
                role='roles/viewer',
                members=['allUsers'])])

    self.client.projects_serviceAccounts.GetIamPolicy.Expect(
        request=self.msgs.IamProjectsServiceAccountsGetIamPolicyRequest(
            resource=('projects/-/serviceAccounts/'
                      'test@test-project.iam.gserviceaccount.com'),
            options_requestedPolicyVersion=
            iam_util.MAX_LIBRARY_IAM_SUPPORTED_VERSION),
        response=policy)

    result = self.Run('iam service-accounts get-iam-policy '
                      'test@test-project.iam.gserviceaccount.com '
                      '--account test2@test-project.iam.gserviceaccount.com')

    self.assertEqual(result, policy)

  def testGetIamPolicyInvalidName(self):
    with self.assertRaisesRegex(
        cli_test_base.MockArgumentError,
        r'Not a valid service account identifier. It should be either a '
        r'numeric string representing the unique_id or an email of the form: '
        r'my-iam-account@somedomain.com or '
        r'my-iam-account@PROJECT_ID.iam.gserviceaccount.com'):
      self.Run('iam service-accounts get-iam-policy test')

  def testGetIamPolicyValidUniqueId(self):
    self.client.projects_serviceAccounts.GetIamPolicy.Expect(
        request=self.msgs.IamProjectsServiceAccountsGetIamPolicyRequest(
            resource='projects/-/serviceAccounts/' + self.sample_unique_id,
            options_requestedPolicyVersion=
            iam_util.MAX_LIBRARY_IAM_SUPPORTED_VERSION),
        response=self.msgs.Policy())
    try:
      self.Run('iam service-accounts get-iam-policy ' + self.sample_unique_id)
    except cli_test_base.MockArgumentError:
      self.fail('get-iam-policy should accept unique ids for service '
                'accounts.')


class GetIamPolicyTestBeta(GetIamPolicyTestGA):

  def SetUp(self):
    self.track = calliope_base.ReleaseTrack.BETA


class GetIamPolicyTestAlpha(GetIamPolicyTestBeta):

  def SetUp(self):
    self.track = calliope_base.ReleaseTrack.ALPHA


if __name__ == '__main__':
  test_case.main()
