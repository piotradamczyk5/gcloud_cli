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
"""Common component for VPN tunnels labels testing."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding
from apitools.base.py.testing import mock
from googlecloudsdk.api_lib.util import apis

from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.core import resources
from tests.lib import cli_test_base
from tests.lib import sdk_test_base


class VpnTunnelsLabelsTestBase(sdk_test_base.WithFakeAuth,
                               cli_test_base.CliTestBase):
  """Base class for VPN tunnels test."""

  def SetUp(self):
    api_name = 'beta'
    self.mock_apitools_client = mock.Client(
        apis.GetClientClass('compute', api_name),
        real_client=apis.GetClientInstance('compute', api_name, no_http=True))
    self.mock_apitools_client.Mock()
    self.addCleanup(self.mock_apitools_client.Unmock)
    self.messages = self.mock_apitools_client.MESSAGES_MODULE

    self.resources = resources.Registry()
    self.resources.RegisterApiByName('compute', api_name)
    self.track = calliope_base.ReleaseTrack.BETA
    self.mock_region_operations = self.mock_apitools_client.regionOperations
    # Patch time.sleep for faster test execution.
    self.StartPatch('time.sleep')

  def _GetVpnTunnelRef(self, name, region=None):
    """Gets a reference to a VPN tunnel.

    Args:
      name: str, name of the VPN tunnel resource.
      region: str, region in which the VPN tunnel is.
    Returns:
      Reference to the VPN tunnel resource.
    """
    params = {'project': self.Project()}
    collection = 'compute.vpnTunnels'
    params['region'] = region

    return self.resources.Parse(name, params=params, collection=collection)

  def _GetOperationRef(self, name, region=None):
    """Gets a reference to an operation.

    Args:
      name: str, name of the operation.
      region: str, region in which the operation is.
    Returns:
      Reference to the operation.
    """
    params = {'project': self.Project(), 'region': region}
    return self.resources.Parse(
        name, params=params, collection='compute.regionOperations')

  def _MakeOperationMessage(self, operation_ref, resource_ref=None):
    """Constructs an Operation message.

    Args:
      operation_ref: Reference to the operation.
      resource_ref: Reference to the resource that the operation modifies.
    Returns:
      An Operation resource.
    """
    return self.messages.Operation(
        name=operation_ref.Name(),
        status=self.messages.Operation.StatusValueValuesEnum.DONE,
        selfLink=operation_ref.SelfLink(),
        targetLink=resource_ref.SelfLink() if resource_ref else None)

  def _MakeVpnTunnelProto(self, labels=None, fingerprint=None):
    """Constructs a VPN tunnel message.

    Args:
      labels: Tuple of labels ((key, value) pairs) on the VPN tunnel.
      fingerprint: str, label fingerprint of the VPN tunnel.
    Returns:
      A VpnTunnel message with the given labels and fingerprint.
    """
    msg = self.messages.VpnTunnel()
    if labels is not None:
      labels_value = msg.LabelsValue
      msg.labels = labels_value(additionalProperties=[
          labels_value.AdditionalProperty(key=pair[0], value=pair[1])
          for pair in labels
      ])
    if fingerprint:
      msg.labelFingerprint = fingerprint
    return msg

  def _MakeLabelsProto(self, labels_value, labels):
    """Constructs a Labels message.

    Args:
      labels_value: A LabelsValue message.
      labels: Tuple of labels ((key, value) pairs) that the VPN tunnel
              should have.
    Returns:
      A VpnTunnel message with the given labels and fingerprint.
    """
    labels_dict = {pair[0]: pair[1] for pair in labels}
    return encoding.DictToAdditionalPropertyMessage(
        labels_dict, labels_value, sort_items=True)

  def _ExpectGetRequest(self, vpn_tunnel_ref, vpn_tunnel=None):
    """Verifies a Get request on a VPN tunnel.

    Args:
      vpn_tunnel_ref: Resource reference for the VPN tunnel.
      vpn_tunnel: The VpnTunnel message expected to be
                          returned.
    """
    service = self.mock_apitools_client.vpnTunnels
    request_type = self.messages.ComputeVpnTunnelsGetRequest

    service.Get.Expect(
        request=request_type(**vpn_tunnel_ref.AsDict()), response=vpn_tunnel)

  def _ExpectOperationGetRequest(self, operation_ref, operation):
    """Verifies a Get request on an operation.

    Args:
      operation_ref: Reference to the operation.
      operation: The Operation message expected to be returned.
    """
    self.mock_region_operations.Get.Expect(
        self.messages.ComputeRegionOperationsGetRequest(
            operation=operation_ref.operation,
            region=operation_ref.region,
            project=self.Project()), operation)

  def _ExpectLabelsSetRequest(self,
                              vpn_tunnel_ref,
                              labels,
                              fingerprint,
                              vpn_tunnel=None):
    """Verifies a SetLabels request on a VPN tunnel.

    Args:
      vpn_tunnel_ref: Resource reference for the VPN tunnel.
      labels: Expected tuple of labels ((key, value) pairs) provided in the
              request.
      fingerprint: str, expected label fingerprint provided in the request.
      vpn_tunnel: The VPN tunnel expected as the response.
    """
    service = self.mock_apitools_client.vpnTunnels
    request_type = self.messages.ComputeVpnTunnelsSetLabelsRequest
    scoped_set_labels_request = self.messages.RegionSetLabelsRequest

    labels_value = self._MakeLabelsProto(scoped_set_labels_request.LabelsValue,
                                         labels)
    request = request_type(
        project=vpn_tunnel_ref.project,
        resource=vpn_tunnel_ref.vpnTunnel,
    )
    request.region = vpn_tunnel_ref.region
    request.regionSetLabelsRequest = scoped_set_labels_request(
        labelFingerprint=fingerprint,
        labels=labels_value,
    )

    service.SetLabels.Expect(request=request, response=vpn_tunnel)
