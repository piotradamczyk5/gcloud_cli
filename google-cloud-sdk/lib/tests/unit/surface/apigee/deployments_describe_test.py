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
"""Tests that exercise the 'gcloud apigee deployments describe' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import json
from googlecloudsdk.calliope.concepts import handlers
from googlecloudsdk.command_lib.apigee import errors
from tests.lib.surface.apigee import base


def _GetCannedDeployment(revision="3"):
  return {
      "environment": "test",
      "apiProxy": "demo",
      "revision": revision,
      "deployStartTime": "1588262386845",
      "basePath": "/"
  }


class DeploymentsDescribeTest(base.ApigeeSurfaceTest):

  def _AddOrganizationListResponse(self):
    canned_organization_response = {
        "organizations": [{
            "organization": "my-org",
            "projectIds": ["my-project"]
        }]
    }
    self.AddHTTPResponse(
        "https://apigee.googleapis.com/v1/organizations",
        status=200,
        body=json.dumps(canned_organization_response))

  def _AddListResponse(self, revisions):
    url = ("https://apigee.googleapis.com/v1/organizations/my-org/environments/"
           "test/apis/demo/deployments")
    response = [_GetCannedDeployment(revision) for revision in revisions]
    self.AddHTTPResponse(url, status=200, body=json.dumps(response))

  def _AddDescribeResponse(self, revision):
    response = {
        "environment": "test",
        "apiProxy": "demo",
        "revision": revision,
        "deployStartTime": "1588368954558",
        "pods": [{
            "podName": "apigee-runtime-unit-test-v120-xfl27",
            "deploymentStatus": "pending",
            "podStatus": "active",
            "podStatusTime": "1588802999368"
        }],
        "basePath": "/"
    }
    url = ("https://apigee.googleapis.com/v1/organizations/my-org/environments/"
           "test/apis/demo/revisions/%s/deployments") % revision
    self.AddHTTPResponse(url, status=200, body=json.dumps(response))
    return response

  def testWithoutOrganization(self):
    with self.assertRaises(handlers.ParseError):
      self.RunApigee("deployments describe --api=demo --environment=test 2")
    self.AssertErrContains(
        "--organization",
        "Must prompt user for an organization name if organization and product "
        "are unknown.")

  def testWithoutAPI(self):
    with self.assertRaises(handlers.ParseError):
      self.RunApigee("deployments describe --organization=my-org "
                     "--environment=test 2")
    self.AssertErrContains(
        "--api", "Must prompt user for a proxy name if none is provided.")

  def testWithExplicitRevision(self):
    expected_output = self._AddDescribeResponse("2")
    self.RunApigee("deployments describe --format=json 2 --organization=my-org "
                   "--environment=test --api=demo")
    self.AssertJsonOutputMatches(
        expected_output, "Must correctly request an explicit revision.")

  def testWithAutomaticRevision(self):
    self._AddOrganizationListResponse()
    self._AddListResponse(["3"])
    expected_output = self._AddDescribeResponse("3")
    self.RunApigee("deployments describe --format=json --project=my-project "
                   "--environment=test --api=demo")
    self.AssertJsonOutputMatches(expected_output,
                                 "Must correctly infer an implicit revision.")

  def testWithAmbiguousRevision(self):
    self._AddOrganizationListResponse()
    self._AddListResponse(["2", "3"])

    with self.assertRaises(errors.AmbiguousRequestError):
      self.RunApigee("deployments describe --format=json --project=my-project "
                     "--environment=test --api=demo")

    self.AssertErrContains("revision: '2'")
    self.AssertErrContains("revision: '3'")

  def testWithNoMatchingImplicitRevision(self):
    self._AddOrganizationListResponse()
    self._AddListResponse([])

    with self.assertRaises(errors.EntityNotFoundError):
      self.RunApigee("deployments describe --format=json --project=my-project "
                     "--environment=test --api=demo")

    self.AssertErrContains("deployment")

  def testWithNoMatchingExplicitRevision(self):
    self._AddOrganizationListResponse()
    url = ("https://apigee.googleapis.com/v1/organizations/my-org/environments/"
           "test/apis/demo/revisions/2/deployments")
    self.AddHTTPResponse(url, status=404, body=json.dumps({}))

    with self.assertRaises(errors.EntityNotFoundError):
      self.RunApigee("deployments describe --format=json --project=my-project "
                     "--environment=test --api=demo 2")

    self.AssertErrContains("deployment")
