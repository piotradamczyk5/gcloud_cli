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

"""Tests for the backend services beta create subcommand."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.backend_services import backend_services_utils
from googlecloudsdk.core import resources
from tests.lib import test_case
from tests.lib.surface.compute import test_base


class CreateTestBase(test_base.BaseTest):

  def SetUp(self):
    self.SelectApi('beta')
    self.track = calliope_base.ReleaseTrack.BETA
    self.resources = resources.REGISTRY.Clone()
    self.resources.RegisterApiByName('compute', 'beta')

  def RunCreate(self, command, use_global=True):
    suffix = ' --global' if use_global else ''
    super(CreateTestBase,
          self).Run('compute backend-services create ' + command + suffix)


class WithHealthcheckApiTest(CreateTestBase):

  def testSimpleCase(self):
    messages = self.messages
    self.RunCreate("""
          my-backend-service
          --health-checks my-health-check-1,my-health-check-2
          --global-health-checks
          --description "My backend service"
        """)

    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check-1'
                    ), (self.compute_uri + '/projects/'
                        'my-project/global/healthChecks/my-health-check-2')
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30),
            project='my-project'))],)

  def testHealthCheckUri(self):
    messages = self.messages
    self.RunCreate("""
        my-backend-service --health-checks
        {uri}/projects/my-project/global/healthChecks/my-health-check
        --global-health-checks
        """.format(uri=self.compute_uri))

    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check')
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30),
            project='my-project'))],)

  def testMixingHealthCheckAndHttpHealthCheck(self):
    with self.AssertRaisesToolExceptionRegexp(
        'Mixing --health-checks with --http-health-checks or with '
        '--https-health-checks is not supported.'):
      self.RunCreate("""
          my-backend-service --health-checks foo
            --http-health-checks bar --global-health-checks
          """)
    self.CheckRequests()

  def testMixingHealthCheckAndHttpsHealthCheck(self):
    with self.AssertRaisesToolExceptionRegexp(
        'Mixing --health-checks with --http-health-checks or with '
        '--https-health-checks is not supported.'):
      self.RunCreate("""
          my-backend-service --health-checks foo
            --https-health-checks bar --global-health-checks
          """)
    self.CheckRequests()

  def testSimpleTcpCase(self):
    messages = self.messages
    self.RunCreate("""
        my-backend-service
          --protocol TCP
          --health-checks my-health-check-1,my-health-check-2
          --global-health-checks
          --description "My backend service"
        """)

    self.CheckRequests(
        [(self.compute.backendServices,
          'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-1'),
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-2')
                  ],
                  name='my-backend-service',
                  portName='tcp',
                  protocol=(messages.BackendService
                            .ProtocolValueValuesEnum.TCP),
                  timeoutSec=30),
              project='my-project'))],
    )

  def testLoadBalancingSchemeInternalSelfManaged(self):
    messages = self.messages
    self.Run("""
        compute backend-services create my-backend-service
          --protocol HTTP
          --health-checks my-health-check-1,my-health-check-2
          --global-health-checks
          --description "My backend service"
          --load-balancing-scheme internal_self_managed
          --global
        """)

    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check-1'),
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check-2')
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                loadBalancingScheme=(
                    messages.BackendService.LoadBalancingSchemeValueValuesEnum.
                    INTERNAL_SELF_MANAGED),
                timeoutSec=30),
            project='my-project'))],)

  def testSimpleSslCase(self):
    messages = self.messages
    self.RunCreate("""
        my-backend-service
          --protocol SSL
          --health-checks my-health-check-1,my-health-check-2
          --global-health-checks
          --description "My backend service"
        """)

    self.CheckRequests(
        [(self.compute.backendServices,
          'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-1'),
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-2')
                  ],
                  name='my-backend-service',
                  portName='ssl',
                  protocol=(messages.BackendService
                            .ProtocolValueValuesEnum.SSL),
                  timeoutSec=30),
              project='my-project'))],
    )

  def testSslWithPortName(self):
    messages = self.messages
    self.RunCreate("""
        my-backend-service
          --protocol SSL
          --health-checks my-health-check
          --global-health-checks
          --port-name ssl1
        """)

    self.CheckRequests(
        [(self.compute.backendServices,
          'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check')
                  ],
                  name='my-backend-service',
                  portName='ssl1',
                  protocol=(messages.BackendService
                            .ProtocolValueValuesEnum.SSL),
                  timeoutSec=30),
              project='my-project'))],
    )

  def testSslWithTimeout(self):
    messages = self.messages
    self.RunCreate("""
        my-backend-service
          --protocol SSL
          --health-checks my-health-check
          --global-health-checks
          --timeout 1m
        """)

    self.CheckRequests(
        [(self.compute.backendServices,
          'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check')
                  ],
                  name='my-backend-service',
                  portName='ssl',
                  protocol=(messages.BackendService
                            .ProtocolValueValuesEnum.SSL),
                  timeoutSec=60),
              project='my-project'))],
    )

  def testSslUriSupport(self):
    messages = self.messages
    self.RunCreate("""
          {uri}/projects/my-project/global/backendServices/my-backend-service
          --protocol SSL
          --health-checks
            {uri}/projects/my-project/global/healthChecks/my-health-check-1,{uri}/projects/my-project/global/healthChecks/my-health-check-2
          --global-health-checks
        """.format(uri=self.compute_uri))

    self.CheckRequests(
        [(self.compute.backendServices,
          'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-1'),
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-2'),
                  ],
                  name='my-backend-service',
                  portName='ssl',
                  protocol=(messages.BackendService
                            .ProtocolValueValuesEnum.SSL),
                  timeoutSec=30),
              project='my-project'))],
    )

  def testInternalWithoutRegionFlag(self):
    with self.AssertRaisesToolExceptionRegexp(
        'Must specify --region for internal load balancer.'):
      self.RunCreate(
          'backend-service-24 '
          '--load-balancing-scheme=internal '
          '--health-checks=main-hc --global-health-checks --protocol=TCP')

  def testInternalWithAllValidFlags(self):
    messages = self.messages

    self.RunCreate(
        'backend-service-1 '
        '--description cheesecake '
        '--load-balancing-scheme internal '
        '--region alaska '
        '--health-checks my-health-check-1 '
        '--global-health-checks '
        '--network default '
        '--connection-draining-timeout 120',
        use_global=False)

    self.CheckRequests([(
        self.compute.regionBackendServices, 'Insert',
        messages.ComputeRegionBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check-1'),
                ],
                name='backend-service-1',
                description='cheesecake',
                loadBalancingScheme=(
                    messages.BackendService.LoadBalancingSchemeValueValuesEnum
                    .INTERNAL),
                network=self.compute_uri +
                '/projects/my-project/global/networks/default',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.TCP),
                connectionDraining=messages.ConnectionDraining(
                    drainingTimeoutSec=120),
                timeoutSec=30,
            ),
            project='my-project',
            region='alaska',
        )
    )],)

  def testSimpleHttp2Case(self):
    messages = self.messages
    self.RunCreate("""
          my-backend-service
          --global
          --protocol HTTP2
          --health-checks my-health-check-1,my-health-check-2
          --global-health-checks
          --description "My backend service"
        """)

    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-1'),
                      (self.compute_uri + '/projects/'
                       'my-project/global/healthChecks/my-health-check-2')
                  ],
                  name='my-backend-service',
                  portName='http2',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP2),
                  timeoutSec=30),
              project='my-project'))],)

  def testSimpleCaseWithHeader(self):
    messages = self.messages
    self.RunCreate("""
          my-backend-service
          --global
          --health-checks my-health-check-1,my-health-check-2
          --global-health-checks
          --description "My backend service"
          --custom-request-header 'Test-Header:'
          --custom-request-header 'Test-Header2: {CLIENT_REGION}'
        """)

    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check-1'),
                    (self.compute_uri + '/projects/'
                     'my-project/global/healthChecks/my-health-check-2')
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30,
                customRequestHeaders=[
                    'Test-Header:', 'Test-Header2: {CLIENT_REGION}'
                ]),
            project='my-project'))],)


class WithConnectionDrainingTimeoutApiTest(CreateTestBase):

  # When no --connection-draining-timeout specified, no default value should be
  # set on this level.
  def testDefault(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
        """)
    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/httpHealthChecks/my-health-check-1'),
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30),
            project='my-project'))],)

  def testConnectionDrainingTimeout(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --connection-draining-timeout 120
        """)
    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/httpHealthChecks/my-health-check-1'),
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30,
                connectionDraining=messages.ConnectionDraining(
                    drainingTimeoutSec=120)),
            project='my-project'))],)

  def testConnectionDrainingTimeoutInMinutes(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --connection-draining-timeout 2m
        """)
    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/httpHealthChecks/my-health-check-1'),
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30,
                connectionDraining=messages.ConnectionDraining(
                    drainingTimeoutSec=120)),
            project='my-project'))],)

  def testConnectionDrainingDisabled(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --connection-draining-timeout 0
        """)
    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/httpHealthChecks/my-health-check-1'),
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30,
                connectionDraining=messages.ConnectionDraining(
                    drainingTimeoutSec=0)),
            project='my-project'))],)


class WithIAPApiTest(CreateTestBase):

  def SetUp(self):
    self._create_service_cmd_line = (
        'backend-service-1 '
        '--http-health-checks my-health-check-1 '
        '--description "My backend service"')
    self._lb_warning = (
        'WARNING: IAP only protects requests that go through the Cloud Load '
        'Balancer. See the IAP documentation for important security best '
        'practices: https://cloud.google.com/iap/\n')
    self._non_https_warning = (
        'WARNING: IAP has been enabled for a backend service that does not use '
        'HTTPS. Data sent from the Load Balancer to your VM will not be '
        'encrypted.\n')

  def CheckResultsWithProtocol(self, expected_message, protocol):
    messages = self.messages
    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                healthChecks=[
                    (self.compute_uri + '/projects/'
                     'my-project/global/httpHealthChecks/my-health-check-1'),
                ],
                iap=expected_message,
                name='backend-service-1',
                portName='http',
                protocol=protocol,
                timeoutSec=30),
            project='my-project'))])

  def CheckResults(self, expected_message):
    self.CheckResultsWithProtocol(
        expected_message,
        self.messages.BackendService.ProtocolValueValuesEnum.HTTP)

  def testWithIAPDisabled(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap disabled')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=False))
    self.AssertErrEquals('')

  def testWithIAPEnabled(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap enabled')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=True))

  def testWithIAPEnabledAndNonHttpsProtocol(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap enabled --protocol=HTTP')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=True))
    self.AssertErrEquals(self._lb_warning + self._non_https_warning)

  def testWithIAPEnabledAndHttpsProtocol(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap enabled --protocol=HTTPS --port-name=http')
    self.CheckResultsWithProtocol(
        self.messages.BackendServiceIAP(enabled=True),
        self.messages.BackendService.ProtocolValueValuesEnum.HTTPS)
    self.AssertErrEquals(self._lb_warning)

  def testWithIAPDisabledAndNonHttpsProtocol(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap disabled --protocol=HTTP')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=False))
    self.AssertErrEquals('')

  def testWithIAPDisabledAndHttpsProtocol(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap disabled --protocol=HTTPS --port-name=http')
    self.CheckResultsWithProtocol(
        self.messages.BackendServiceIAP(enabled=False),
        self.messages.BackendService.ProtocolValueValuesEnum.HTTPS)
    self.AssertErrEquals('')

  def testWithIAPEnabledWithCredentials(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap enabled,oauth2-client-id=CLIENTID,oauth2-client-secret=SECRET')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=True,
        oauth2ClientId='CLIENTID',
        oauth2ClientSecret='SECRET'))

  def testWithIAPEnabledWithCredentialsWithEmbeddedEquals(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap enabled,oauth2-client-id=CLIENT=ID,'
        'oauth2-client-secret=SEC=RET')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=True,
        oauth2ClientId='CLIENT=ID',
        oauth2ClientSecret='SEC=RET'))

  def testWithIapCredentialsOnly(self):
    self.RunCreate(
        self._create_service_cmd_line +
        ' --iap oauth2-client-id=CLIENT=ID,oauth2-client-secret=SEC=RET')
    self.CheckResults(self.messages.BackendServiceIAP(
        enabled=False,
        oauth2ClientId='CLIENT=ID',
        oauth2ClientSecret='SEC=RET'))

  def testInvalidIAPEmpty(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        r'^Invalid value for \[--iap\]: Must provide value when specifying '
        r'--iap$',
        self.RunCreate, self._create_service_cmd_line + ' --iap=""')

  def testInvalidIapArgCombinationEnabledDisabled(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--iap\\]: Must specify only one '
        'of \\[enabled\\] or \\[disabled\\]$',
        self.RunCreate,
        self._create_service_cmd_line + ' --iap enabled,disabled')

  def testInvalidIapArgCombinationEnabledOnlyClientId(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--iap\\]: Both \\[oauth2-client-id\\] and '
        '\\[oauth2-client-secret\\] must be specified together$',
        self.RunCreate,
        self._create_service_cmd_line +
        ' --iap enabled,oauth2-client-id=CLIENTID')

  def testInvalidIapArgCombinationEnabledOnlyClientSecret(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--iap\\]: Both \\[oauth2-client-id\\] and '
        '\\[oauth2-client-secret\\] must be specified together$',
        self.RunCreate,
        self._create_service_cmd_line +
        ' --iap enabled,oauth2-client-secret=SECRET')

  def testInvalidIapArgCombinationEmptyIdValue(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--iap\\]: Both \\[oauth2-client-id\\] and '
        '\\[oauth2-client-secret\\] must be specified together$',
        self.RunCreate,
        self._create_service_cmd_line +
        ' --iap enabled,oauth2-client-id=,oauth2-client-secret=SECRET')

  def testInvalidIapArgCombinationEmptySecretValue(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--iap\\]: Both \\[oauth2-client-id\\] and '
        '\\[oauth2-client-secret\\] must be specified together$',
        self.RunCreate,
        self._create_service_cmd_line +
        ' --iap enabled,oauth2-client-id=CLIENTID,oauth2-client-secret=')

  def testInvalidIapArgInvalidSubArg(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        r'^Invalid value for \[--iap\]: Invalid sub-argument \'invalid-arg1\'$',
        self.RunCreate,
        self._create_service_cmd_line +
        ' --iap enabled,invalid-arg1=VAL1,invalid-arg2=VAL2')


class WithCustomCacheKeyApiTest(CreateTestBase):

  # When no custom cache keys flags are specified, no custom cache key flags
  # should appear in the request.
  def testDefault(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
        """)
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='my-backend-service',
                  portName='http',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP),
                  timeoutSec=30),
              project='my-project'))],)

  def testCacheKeyExcludeHost(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --no-cache-key-include-host
        """)
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='my-backend-service',
                  portName='http',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP),
                  timeoutSec=30,
                  cdnPolicy=messages.BackendServiceCdnPolicy(
                      cacheKeyPolicy=messages.CacheKeyPolicy(
                          includeHost=False,
                          includeProtocol=True,
                          includeQueryString=True))),
              project='my-project'))],)

  def testCacheKeyExcludeProtocol(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --no-cache-key-include-protocol
        """)
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='my-backend-service',
                  portName='http',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP),
                  timeoutSec=30,
                  cdnPolicy=messages.BackendServiceCdnPolicy(
                      cacheKeyPolicy=messages.CacheKeyPolicy(
                          includeHost=True,
                          includeProtocol=False,
                          includeQueryString=True))),
              project='my-project'))],)

  def testCacheKeyExcludeQueryString(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --no-cache-key-include-query-string
        """)
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='my-backend-service',
                  portName='http',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP),
                  timeoutSec=30,
                  cdnPolicy=messages.BackendServiceCdnPolicy(
                      cacheKeyPolicy=messages.CacheKeyPolicy(
                          includeHost=True,
                          includeProtocol=True,
                          includeQueryString=False))),
              project='my-project'))],)

  def testCacheKeyQueryStringWhitelist(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --cache-key-query-string-whitelist=contentid,language
        """)
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='my-backend-service',
                  portName='http',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP),
                  timeoutSec=30,
                  cdnPolicy=messages.BackendServiceCdnPolicy(
                      cacheKeyPolicy=messages.CacheKeyPolicy(
                          includeHost=True,
                          includeProtocol=True,
                          includeQueryString=True,
                          queryStringWhitelist=['contentid', 'language']))),
              project='my-project'))],)

  def testCacheKeyQueryStringBlacklist(self):
    messages = self.messages

    self.RunCreate("""
        my-backend-service
          --http-health-checks my-health-check-1
          --description "My backend service"
          --cache-key-query-string-blacklist=campaign
        """)
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='my-backend-service',
                  portName='http',
                  protocol=(
                      messages.BackendService.ProtocolValueValuesEnum.HTTP),
                  timeoutSec=30,
                  cdnPolicy=messages.BackendServiceCdnPolicy(
                      cacheKeyPolicy=messages.CacheKeyPolicy(
                          includeHost=True,
                          includeProtocol=True,
                          includeQueryString=True,
                          queryStringBlacklist=['campaign']))),
              project='my-project'))],)

  def testEnableWhitelistWithExcludeQueryString(self):
    with self.assertRaisesRegex(
        backend_services_utils.CacheKeyQueryStringException,
        'cache-key-query-string-whitelist and cache-key-query-string-blacklist'
        ' may only be set when cache-key-include-query-string is enabled.'):
      self.RunCreate("""
          my-backend-service --health-checks my-health-check
            --global-health-checks
            --no-cache-key-include-query-string
            --cache-key-query-string-whitelist=contentid,language
          """)
    self.CheckRequests()

  def testEnableBlacklistWithExcludeQueryString(self):
    with self.assertRaisesRegex(
        backend_services_utils.CacheKeyQueryStringException,
        'cache-key-query-string-whitelist and cache-key-query-string-blacklist'
        ' may only be set when cache-key-include-query-string is enabled.'):
      self.RunCreate("""
          my-backend-service --health-checks my-health-check
            --global-health-checks
            --no-cache-key-include-query-string
            --cache-key-query-string-blacklist=campaignid
          """)
    self.CheckRequests()


class WithCdnSignedUrlApiTest(CreateTestBase):

  def CheckRequestMadeWithCdnPolicy(self, expected_message):
    """Verifies the request was made with the expected CDN policy."""
    messages = self.messages
    self.CheckRequests(
        [(self.compute.backendServices, 'Insert',
          messages.ComputeBackendServicesInsertRequest(
              backendService=messages.BackendService(
                  backends=[],
                  cdnPolicy=expected_message,
                  description='My backend service',
                  healthChecks=[
                      (self.compute_uri + '/projects/'
                       'my-project/global/httpHealthChecks/my-health-check-1'),
                  ],
                  name='backend-service-1',
                  portName='http',
                  protocol=messages.BackendService.ProtocolValueValuesEnum.HTTP,
                  timeoutSec=30),
              project='my-project'))])

  def testCreateWithoutCacheMaxAge(self):
    """Tests creating backend service without cache max age."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        """)
    self.CheckRequestMadeWithCdnPolicy(None)

  def testCreateWithCacheMaxAgeZero(self):
    """Tests creating backend service with cache max age of 0."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        --signed-url-cache-max-age 0
        """)
    self.CheckRequestMadeWithCdnPolicy(
        self.messages.BackendServiceCdnPolicy(signedUrlCacheMaxAgeSec=0))

  def testCreateWithCacheMaxAgeSeconds(self):
    """Tests creating backend service with cache max age in seconds."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        --signed-url-cache-max-age 7890s
        """)
    self.CheckRequestMadeWithCdnPolicy(
        self.messages.BackendServiceCdnPolicy(signedUrlCacheMaxAgeSec=7890))

  def testCreateWithCacheMaxAgeMinutes(self):
    """Tests creating backend service with cache max age in minutes."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        --signed-url-cache-max-age 234m
        """)
    self.CheckRequestMadeWithCdnPolicy(
        self.messages.BackendServiceCdnPolicy(signedUrlCacheMaxAgeSec=234 * 60))

  def testCreateWithCacheMaxAgeHours(self):
    """Tests creating backend service with cache max age in hours."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        --signed-url-cache-max-age 38h
        """)
    self.CheckRequestMadeWithCdnPolicy(
        self.messages.BackendServiceCdnPolicy(signedUrlCacheMaxAgeSec=38 * 60 *
                                              60))

  def testCreateWithCacheMaxAgeDays(self):
    """Tests creating backend service with cache max age in days."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        --signed-url-cache-max-age 99d
        """)
    self.CheckRequestMadeWithCdnPolicy(
        self.messages.BackendServiceCdnPolicy(signedUrlCacheMaxAgeSec=99 * 24 *
                                              60 * 60))

  def testSetInvalidCacheMaxAge(self):
    """Tests creating backend service with an invalid cache max age."""
    with self.AssertRaisesArgumentErrorRegexp(
        "argument --signed-url-cache-max-age: Failed to parse duration: "
        "Duration unit 'invalid-value' must be preceded by a number"):
      self.Run("""
          compute backend-services create backend-service-1
          --global
          --http-health-checks my-health-check-1
          --signed-url-cache-max-age invalid-value
          """)

  def testSetCacheMaxAgeNegative(self):
    """Tests creating backend service with a negative cache max age."""
    with self.AssertRaisesArgumentErrorRegexp(
        'argument --signed-url-cache-max-age: value must be greater than or '
        'equal to 0; received: -1'):
      self.Run("""
          compute backend-services create backend-service-1
          --global
          --http-health-checks my-health-check-1
          --description "My backend service"
          --signed-url-cache-max-age -1
          """)

  def testWithCacheMaxAgeAndCacheKeyPolicy(self):
    """Tests creating backend service with both cache max age and cache keys."""
    self.Run("""
        compute backend-services create backend-service-1
        --global
        --http-health-checks my-health-check-1
        --description "My backend service"
        --signed-url-cache-max-age 1234
        --cache-key-query-string-whitelist=foo,bar,baz
        """)
    self.CheckRequestMadeWithCdnPolicy(
        self.messages.BackendServiceCdnPolicy(
            signedUrlCacheMaxAgeSec=1234,
            cacheKeyPolicy=self.messages.CacheKeyPolicy(
                includeHost=True,
                includeProtocol=True,
                includeQueryString=True,
                queryStringWhitelist=['foo', 'bar', 'baz'])))


class WithFailoverPolicyApiTest(CreateTestBase):

  def SetUp(self):
    self._create_service_cmd_line = (
        """compute backend-services create my-backend-service
           --health-checks my-health-check-1
           --global-health-checks
           --description "My backend service"
           --region us-central1""")

  def CheckResults(self, expected_message=None):
    messages = self.messages

    self.CheckRequests([
        (self.compute.regionBackendServices, 'Insert',
         messages.ComputeRegionBackendServicesInsertRequest(
             backendService=messages.BackendService(
                 backends=[],
                 description='My backend service',
                 failoverPolicy=expected_message,
                 healthChecks=[
                     self.resources.Create(
                         'compute.healthChecks',
                         healthCheck='my-health-check-1',
                         project='my-project').SelfLink(),
                 ],
                 loadBalancingScheme=(
                     messages.BackendService.LoadBalancingSchemeValueValuesEnum.
                     INTERNAL),
                 name='my-backend-service',
                 protocol=(messages.BackendService.ProtocolValueValuesEnum.TCP),
                 timeoutSec=30),
             project='my-project',
             region='us-central1'))
    ],)

  def testEnableFailoverOptions(self):
    self.Run(self._create_service_cmd_line + ' --load-balancing-scheme internal'
             ' --no-connection-drain-on-failover'
             ' --drop-traffic-if-unhealthy'
             ' --failover-ratio 0.5')
    self.CheckResults(
        self.messages.BackendServiceFailoverPolicy(
            disableConnectionDrainOnFailover=True,
            dropTrafficIfUnhealthy=True,
            failoverRatio=0.5))

  def testDisableFailoverOptions(self):
    self.Run(self._create_service_cmd_line + ' --load-balancing-scheme internal'
             ' --connection-drain-on-failover'
             ' --no-drop-traffic-if-unhealthy'
             ' --failover-ratio 0.5')
    self.CheckResults(
        self.messages.BackendServiceFailoverPolicy(
            disableConnectionDrainOnFailover=False,
            dropTrafficIfUnhealthy=False,
            failoverRatio=0.5))

  def testCannotSpecifyFailoverPolicyForGlobalBackendService(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--global\\]: cannot specify failover policies'
        ' for global backend services.', self.Run,
        'compute backend-services create backend-service-1'
        ' --http-health-checks my-health-check-1'
        ' --description "My backend service"'
        ' --global'
        ' --connection-drain-on-failover')

  def testInvalidLoadBalancingSchemeWithInternalFailoverOptions(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--load-balancing-scheme\\]: can only specify '
        '--connection-drain-on-failover or --drop-traffic-if-unhealthy'
        ' if the load balancing scheme is INTERNAL.', self.Run,
        self._create_service_cmd_line + ' --protocol TCP' +
        ' --drop-traffic-if-unhealthy')

  def testInvalidProtocolWithConnectionDrainOnFailover(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--protocol\\]: can only specify '
        '--connection-drain-on-failover if the protocol is TCP.',
        self.Run,
        self._create_service_cmd_line + ' --load-balancing-scheme INTERNAL' +
        ' --protocol SSL' + ' --connection-drain-on-failover')


class WithLogConfigApiTest(CreateTestBase):

  def SetUp(self):
    self._create_service_cmd_line = (
        """compute backend-services create my-backend-service
           --health-checks my-health-check-1
           --global-health-checks
           --description "My backend service"
           --global""")

  def CheckResults(self, expected_message=None):
    messages = self.messages

    self.CheckRequests([(
        self.compute.backendServices, 'Insert',
        messages.ComputeBackendServicesInsertRequest(
            backendService=messages.BackendService(
                backends=[],
                description='My backend service',
                logConfig=expected_message,
                healthChecks=[
                    self.resources.Create(
                        'compute.healthChecks',
                        healthCheck='my-health-check-1',
                        project='my-project').SelfLink(),
                ],
                name='my-backend-service',
                portName='http',
                protocol=(messages.BackendService.ProtocolValueValuesEnum.HTTP),
                timeoutSec=30),
            project='my-project'))],)

  def testEnableLogging(self):
    self.Run(self._create_service_cmd_line + ' --load-balancing-scheme external'
             ' --protocol HTTP'
             ' --enable-logging'
             ' --logging-sample-rate 0.7')
    self.CheckResults(
        self.messages.BackendServiceLogConfig(enable=True, sampleRate=0.7))

  def testDisableLogging(self):
    self.Run(self._create_service_cmd_line + ' --load-balancing-scheme external'
             ' --protocol HTTP'
             ' --no-enable-logging'
             ' --logging-sample-rate 0.0')
    self.CheckResults(
        self.messages.BackendServiceLogConfig(enable=False, sampleRate=0.0))

  def testInvalidProtocolWithLogConfig(self):
    self.assertRaisesRegex(
        exceptions.InvalidArgumentException,
        '^Invalid value for \\[--protocol\\]: can only specify --enable-logging'
        ' or --logging-sample-rate if the protocol is HTTP/HTTPS/HTTP2.',
        self.Run,
        self._create_service_cmd_line + ' --load-balancing-scheme external' +
        ' --protocol TCP' + ' --enable-logging')


if __name__ == '__main__':
  test_case.main()
