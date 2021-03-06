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

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os

from apitools.base.py import encoding
from googlecloudsdk.api_lib import tasks as tasks_api_lib
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.tasks import app
from googlecloudsdk.command_lib.tasks import constants
from googlecloudsdk.command_lib.tasks import flags
from googlecloudsdk.command_lib.tasks import parsers
from googlecloudsdk.command_lib.util import time_util
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources
from tests.lib import cli_test_base
from tests.lib import sdk_test_base
from tests.lib import test_case
from tests.lib.calliope import util as calliope_test_util

_ALPHA_MESSAGES_MODULE = apis.GetMessagesModule(tasks_api_lib.API_NAME,
                                                tasks_api_lib.ALPHA_API_VERSION)
_BETA_MESSAGES_MODULE = apis.GetMessagesModule(tasks_api_lib.API_NAME,
                                               tasks_api_lib.BETA_API_VERSION)
_MESSAGES_MODULE = apis.GetMessagesModule(tasks_api_lib.API_NAME,
                                          tasks_api_lib.GA_API_VERSION)
_SELF_LINK_PREFIX = 'https://{}.googleapis.com/{}'.format(
    tasks_api_lib.API_NAME, tasks_api_lib.GA_API_VERSION)


class ParseLocationTest(sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.project.Set('my-project')

  def testParseLocationId(self):
    expected_self_link = '{}/projects/my-project/locations/us-central'.format(
        _SELF_LINK_PREFIX)
    actual_location_ref = parsers.ParseLocation('us-central')
    self.assertEqual(actual_location_ref.SelfLink(), expected_self_link)

  def testParseLocationUri(self):
    expected_self_link = '{}/projects/my-project/locations/us-central'.format(
        _SELF_LINK_PREFIX)
    actual_location_ref = parsers.ParseLocation(expected_self_link)
    self.assertEqual(actual_location_ref.SelfLink(), expected_self_link)

  def testParseLocationUri_DifferentProject(self):
    expected_self_link = (
        '{}/projects/other-project/locations/us-central'.format(
            _SELF_LINK_PREFIX))
    actual_location_ref = parsers.ParseLocation(expected_self_link)
    self.assertEqual(actual_location_ref.SelfLink(), expected_self_link)

  def testParseLocationRelative(self):
    expected_self_link = '{}/projects/my-project/locations/us-central'.format(
        _SELF_LINK_PREFIX)
    actual_location_ref = parsers.ParseLocation(
        'projects/my-project/locations/us-central')
    self.assertEqual(actual_location_ref.SelfLink(), expected_self_link)


class ParseQueueTest(sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.project.Set('my-project')
    self.StartObjectPatch(app,
                          'ResolveAppLocation').return_value = 'us-central1'

  def testParseQueueId(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central1/queues/my-queue'.format(
            _SELF_LINK_PREFIX))
    actual_queue_ref = parsers.ParseQueue('my-queue')
    self.assertEqual(actual_queue_ref.SelfLink(), expected_self_link)

  def testParseQueueId_NoProject(self):
    properties.VALUES.core.project.Set(None)
    with self.assertRaises(properties.RequiredPropertyError):
      parsers.ParseQueue('my-queue')

  def testParseQueueUri(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central1/queues/my-queue'.format(
            _SELF_LINK_PREFIX))
    actual_queue_ref = parsers.ParseQueue(expected_self_link)
    self.assertEqual(actual_queue_ref.SelfLink(), expected_self_link)

  def testParseQueueUri_DifferentProject(self):
    expected_self_link = (
        '{}/projects/other-project/locations/us-central1/'
        'queues/my-queue'.format(_SELF_LINK_PREFIX))
    actual_queue_ref = parsers.ParseQueue(expected_self_link)
    self.assertEqual(actual_queue_ref.SelfLink(), expected_self_link)

  def testParseQueueRelative(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central1/queues/my-queue'.format(
            _SELF_LINK_PREFIX))
    actual_queue_ref = parsers.ParseQueue(
        'projects/my-project/locations/us-central1/queues/my-queue')
    self.assertEqual(actual_queue_ref.SelfLink(), expected_self_link)

  def testParseQueueId_WithLocation(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central2/queues/my-queue'.format(
            _SELF_LINK_PREFIX))
    actual_queue_ref = parsers.ParseQueue('my-queue', location='us-central2')
    self.assertEqual(actual_queue_ref.SelfLink(), expected_self_link)


class ExtractLocationRefFromQueueRefTest(test_case.Base):

  def testExtractLocationRef(self):
    expected_location_ref = resources.REGISTRY.Parse(
        '{}/projects/my-project/locations/us-central'.format(_SELF_LINK_PREFIX),
        collection=constants.LOCATIONS_COLLECTION)
    queue_ref = resources.REGISTRY.Parse(
        '{}/projects/my-project/locations/us-central/queues/my-queue'.format(
            _SELF_LINK_PREFIX),
        collection=constants.QUEUES_COLLECTION)
    actual_location_ref = parsers.ExtractLocationRefFromQueueRef(queue_ref)
    self.assertEqual(actual_location_ref, expected_location_ref)


class ParseTaskTest(sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.project.Set('my-project')
    self.queue_ref = resources.REGISTRY.Create(
        'cloudtasks.projects.locations.queues', locationsId='us-central1',
        projectsId='my-project', queuesId='my-queue')

  def testParseTaskId(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central1/queues/my-queue'
        '/tasks/my-task'.format(_SELF_LINK_PREFIX))
    actual_task_ref = parsers.ParseTask('my-task', self.queue_ref)
    self.assertEqual(actual_task_ref.SelfLink(), expected_self_link)

  def testParseTaskId_NoQueueRef(self):
    with self.assertRaises(parsers.FullTaskUnspecifiedError):
      parsers.ParseTask('my-task')

  def testParseTaskUri(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central1/queues/my-queue'
        '/tasks/my-task'.format(_SELF_LINK_PREFIX))
    actual_task_ref = parsers.ParseTask(expected_self_link)
    self.assertEqual(actual_task_ref.SelfLink(), expected_self_link)

  def testParseTaskUri_DifferentProject(self):
    expected_self_link = (
        '{}/projects/other-project/locations/us-central1/queues/my-queue'
        '/tasks/my-task'.format(_SELF_LINK_PREFIX))
    actual_task_ref = parsers.ParseTask(expected_self_link)
    self.assertEqual(actual_task_ref.SelfLink(), expected_self_link)

  def testParseTaskRelative(self):
    expected_self_link = (
        '{}/projects/my-project/locations/us-central1/queues/my-queue'
        '/tasks/my-task'.format(_SELF_LINK_PREFIX))
    actual_task_ref = parsers.ParseTask(
        'projects/my-project/locations/us-central1/queues/my-queue'
        '/tasks/my-task')
    self.assertEqual(actual_task_ref.SelfLink(), expected_self_link)


class ParseArgsTestBase(cli_test_base.CliTestBase):

  def SetUp(self):
    self.parser = calliope_test_util.ArgumentParser()


class ParseCreateOrUpdatePullQueueArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddCreatePullQueueFlags(self.parser)

  def testParseCreateOrUpdateQueueArgs_NoArgs(self):
    expected_config = _ALPHA_MESSAGES_MODULE.Queue()
    expected_config.pullTarget = _ALPHA_MESSAGES_MODULE.PullTarget()
    args = self.parser.parse_args([])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PULL_QUEUE, _ALPHA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.ALPHA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateOrUpdateQueueArgs_AllArgs(self):
    expected_config = _ALPHA_MESSAGES_MODULE.Queue()
    expected_config.retryConfig = _ALPHA_MESSAGES_MODULE.RetryConfig(
        maxAttempts=10, maxRetryDuration='5s')
    expected_config.pullTarget = _ALPHA_MESSAGES_MODULE.PullTarget()
    args = self.parser.parse_args(['--max-attempts=10',
                                   '--max-retry-duration=5s'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PULL_QUEUE, _ALPHA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.ALPHA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateOrUpdateQueueArgs_AllArgs_MaxAttemptsUnlimited(self):
    expected_config = _ALPHA_MESSAGES_MODULE.Queue()
    expected_config.retryConfig = _ALPHA_MESSAGES_MODULE.RetryConfig(
        unlimitedAttempts=True, maxRetryDuration='5s')
    expected_config.pullTarget = _ALPHA_MESSAGES_MODULE.PullTarget()
    args = self.parser.parse_args(['--max-attempts=unlimited',
                                   '--max-retry-duration=5s'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PULL_QUEUE, _ALPHA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.ALPHA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateOrUpdateQueueArgs_IncludePushArgs(self):
    with self.AssertRaisesArgumentErrorMatches('unrecognized arguments:'):
      self.parser.parse_args(['--max-attempts=10',
                              '--max-retry-duration=5s',
                              '--max-doublings=4',
                              '--min-backoff=1s',
                              '--max-backoff=10s',
                              '--max-tasks-dispatched-per-second=100',
                              '--max-concurrent-tasks=10',
                              '--routing-override=service:abc'])


class ParseLeaseTasksArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddFilterLeasedTasksFlag(self.parser)

  def testParseTasksLeaseFilterFlags_Mutex(self):
    with self.AssertRaisesArgumentErrorMatches(
        'argument --oldest-tag: At most one of --oldest-tag | --tag '
        'may be specified.'):
      self.parser.parse_args(['--oldest-tag', '--tag=tag'])


class ParseCreateOrUpdatePushQueueArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddCreatePushQueueFlags(self.parser)

  def testParseCreateOrUpdateQueueArgs_NoArgs(self):
    expected_config = _MESSAGES_MODULE.Queue()
    args = self.parser.parse_args([])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _MESSAGES_MODULE)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateOrUpdateQueueArgs_AllArgs(self):
    expected_config = _MESSAGES_MODULE.Queue()
    expected_config.retryConfig = _MESSAGES_MODULE.RetryConfig(
        maxAttempts=10, maxRetryDuration='5s', maxDoublings=4, minBackoff='1s',
        maxBackoff='10s')
    expected_config.rateLimits = _MESSAGES_MODULE.RateLimits(
        maxDispatchesPerSecond=100, maxConcurrentDispatches=10)
    expected_config.appEngineRoutingOverride = {'service': 'abc'}
    args = self.parser.parse_args(['--max-attempts=10',
                                   '--max-retry-duration=5s',
                                   '--max-doublings=4',
                                   '--min-backoff=1s',
                                   '--max-backoff=10s',
                                   '--max-dispatches-per-second=100',
                                   '--max-concurrent-dispatches=10',
                                   '--routing-override=service:abc'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _MESSAGES_MODULE)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateOrUpdateQueueArgs_AllArgs_MaxAttemptsUnlimited(self):
    expected_config = _MESSAGES_MODULE.Queue()
    expected_config.retryConfig = _MESSAGES_MODULE.RetryConfig(
        maxAttempts=-1, maxRetryDuration='5s', maxDoublings=4,
        minBackoff='1s', maxBackoff='10s')
    expected_config.rateLimits = _MESSAGES_MODULE.RateLimits(
        maxDispatchesPerSecond=100, maxConcurrentDispatches=10)
    expected_config.appEngineRoutingOverride = {'service': 'abc'}
    args = self.parser.parse_args(['--max-attempts=unlimited',
                                   '--max-retry-duration=5s',
                                   '--max-doublings=4',
                                   '--min-backoff=1s',
                                   '--max-backoff=10s',
                                   '--max-dispatches-per-second=100',
                                   '--max-concurrent-dispatches=10',
                                   '--routing-override=service:abc'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _MESSAGES_MODULE)
    self.assertEqual(actual_config, expected_config)

  def testAppEngineRoutingOverrideValidator(self):
    with self.AssertRaisesArgumentErrorMatches(
        'Only the following keys are valid for routing'):
      self.parser.parse_args(['--routing-override=target:abc'])


class ParseCreateOrUpdateBetaPushQueueArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddCreatePushQueueFlags(self.parser,
                                  release_track=base.ReleaseTrack.BETA)

  def testParseBetaCreateOrUpdateQueueArgs_NoArgs(self):
    expected_config = _BETA_MESSAGES_MODULE.Queue()
    expected_config.appEngineHttpQueue = (
        _BETA_MESSAGES_MODULE.AppEngineHttpQueue())
    expected_config.type = _BETA_MESSAGES_MODULE.Queue.TypeValueValuesEnum.PUSH
    args = self.parser.parse_args([])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseBetaCreateOrUpdateQueueArgs_AllArgs(self):
    expected_config = _BETA_MESSAGES_MODULE.Queue()
    expected_config.retryConfig = _BETA_MESSAGES_MODULE.RetryConfig(
        maxAttempts=10, maxRetryDuration='5s', maxDoublings=4, minBackoff='1s',
        maxBackoff='10s')
    expected_config.rateLimits = _BETA_MESSAGES_MODULE.RateLimits(
        maxDispatchesPerSecond=100, maxConcurrentDispatches=10)
    expected_config.stackdriverLoggingConfig = (
        _BETA_MESSAGES_MODULE.StackdriverLoggingConfig(samplingRatio=0.5))
    expected_config.appEngineHttpQueue = _BETA_MESSAGES_MODULE.AppEngineHttpQueue(
        appEngineRoutingOverride={'service': 'abc'})
    expected_config.type = _BETA_MESSAGES_MODULE.Queue.TypeValueValuesEnum.PUSH
    args = self.parser.parse_args(['--log-sampling-ratio=0.5',
                                   '--max-attempts=10',
                                   '--max-retry-duration=5s',
                                   '--max-doublings=4',
                                   '--min-backoff=1s',
                                   '--max-backoff=10s',
                                   '--max-dispatches-per-second=100',
                                   '--max-concurrent-dispatches=10',
                                   '--routing-override=service:abc'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseBetaCreateOrUpdateQueueArgs_AllArgs_MaxAttemptsUnlimited(self):
    expected_config = _BETA_MESSAGES_MODULE.Queue()
    expected_config.retryConfig = _BETA_MESSAGES_MODULE.RetryConfig(
        maxAttempts=-1, maxRetryDuration='5s', maxDoublings=4,
        minBackoff='1s', maxBackoff='10s')
    expected_config.rateLimits = _BETA_MESSAGES_MODULE.RateLimits(
        maxDispatchesPerSecond=100, maxConcurrentDispatches=10)
    expected_config.stackdriverLoggingConfig = (
        _BETA_MESSAGES_MODULE.StackdriverLoggingConfig(samplingRatio=0.5))
    expected_config.appEngineHttpQueue = _BETA_MESSAGES_MODULE.AppEngineHttpQueue(
        appEngineRoutingOverride={'service': 'abc'})
    expected_config.type = _BETA_MESSAGES_MODULE.Queue.TypeValueValuesEnum.PUSH
    args = self.parser.parse_args(['--log-sampling-ratio=0.5',
                                   '--max-attempts=unlimited',
                                   '--max-retry-duration=5s',
                                   '--max-doublings=4',
                                   '--min-backoff=1s',
                                   '--max-backoff=10s',
                                   '--max-dispatches-per-second=100',
                                   '--max-concurrent-dispatches=10',
                                   '--routing-override=service:abc'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)


class ParseClearQueueFieldsTest(ParseArgsTestBase):

  def testParseClearPullFlags(self):
    flags.AddUpdatePullQueueFlags(self.parser)
    expected_config = _ALPHA_MESSAGES_MODULE.Queue(
        retryConfig=_ALPHA_MESSAGES_MODULE.RetryConfig())
    args = self.parser.parse_args(['--clear-max-attempts',
                                   '--clear-max-retry-duration'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args,
        constants.PULL_QUEUE,
        _ALPHA_MESSAGES_MODULE,
        is_update=True,
        release_track=base.ReleaseTrack.ALPHA)
    self.assertEqual(actual_config, expected_config)

  def testParseBetaClearPushFlags(self):
    flags.AddUpdatePushQueueFlags(self.parser,
                                  release_track=base.ReleaseTrack.BETA)
    expected_config = _BETA_MESSAGES_MODULE.Queue(
        retryConfig=_BETA_MESSAGES_MODULE.RetryConfig(),
        rateLimits=_BETA_MESSAGES_MODULE.RateLimits(),
        stackdriverLoggingConfig=(
            _BETA_MESSAGES_MODULE.StackdriverLoggingConfig()),
        appEngineHttpQueue=_BETA_MESSAGES_MODULE.AppEngineHttpQueue(
            appEngineRoutingOverride=_BETA_MESSAGES_MODULE.AppEngineRouting()),
        type=_BETA_MESSAGES_MODULE.Queue.TypeValueValuesEnum.PUSH)
    args = self.parser.parse_args(['--clear-log-sampling-ratio',
                                   '--clear-max-attempts',
                                   '--clear-max-retry-duration',
                                   '--clear-max-doublings',
                                   '--clear-min-backoff',
                                   '--clear-max-backoff',
                                   '--clear-max-dispatches-per-second',
                                   '--clear-max-concurrent-dispatches',
                                   '--clear-routing-override'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _BETA_MESSAGES_MODULE, is_update=True,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseClearPushFlags(self):
    flags.AddUpdatePushQueueFlags(self.parser)
    expected_config = _MESSAGES_MODULE.Queue(
        retryConfig=_MESSAGES_MODULE.RetryConfig(),
        rateLimits=_MESSAGES_MODULE.RateLimits(),
        appEngineRoutingOverride=_MESSAGES_MODULE.AppEngineRouting())
    args = self.parser.parse_args(['--clear-max-attempts',
                                   '--clear-max-retry-duration',
                                   '--clear-max-doublings',
                                   '--clear-min-backoff',
                                   '--clear-max-backoff',
                                   '--clear-max-dispatches-per-second',
                                   '--clear-max-concurrent-dispatches',
                                   '--clear-routing-override'])
    actual_config = parsers.ParseCreateOrUpdateQueueArgs(
        args, constants.PUSH_QUEUE, _MESSAGES_MODULE, is_update=True)
    self.assertEqual(actual_config, expected_config)


class ParsePullTaskArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddCreatePullTaskFlags(self.parser)
    self.schedule_time = time_util.CalculateExpiration(20)

  def testParseCreateTaskArgs_NoArgs(self):
    with self.AssertRaisesArgumentErrorMatches('--queue: Must be specified'):
      self.parser.parse_args([])

  def testParseCreateTaskArgs_AllArgs_PayloadContent(self):
    expected_config = _ALPHA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    expected_config.pullMessage = _ALPHA_MESSAGES_MODULE.PullMessage(
        tag='tag', payload=b'payload')
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time), '--tag=tag',
        '--payload-content=payload', '--queue=queue_id', 'my-task'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.PULL_TASK, _ALPHA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.ALPHA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_AllArgs_PayloadFile(self):
    expected_config = _ALPHA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    expected_config.pullMessage = _ALPHA_MESSAGES_MODULE.PullMessage(
        tag='tag', payload=b'payload')
    self.Touch(self.temp_path, 'payload.txt', contents='payload')
    payload_file = os.path.join(self.temp_path, 'payload.txt')
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time), '--tag=tag',
        '--queue=queue_name', 'my-task',
        '--payload-file={}'.format(payload_file)
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.PULL_TASK, _ALPHA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.ALPHA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_IncludeAppEngineArgs(self):
    with self.AssertRaisesArgumentErrorMatches('unrecognized arguments:'):
      self.parser.parse_args([
          '--schedule-time={}'.format(
              self.schedule_time), '--tag=tag', '--queue=queue_name', 'my-task',
          '--payload-content=payload', '--method=POST', '--url=/paths/a/',
          '--header=header:value', '--routing=service:abc'
      ])


class ParseAppEngineTaskArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddCreateAppEngineTaskFlags(self.parser)
    self.schedule_time = time_util.CalculateExpiration(20)

  def testParseCreateTaskArgs_NoArgs(self):
    with self.AssertRaisesArgumentErrorMatches(
        'argument --queue: Must be specified.'):
      self.parser.parse_args([])

  def testParseCreateTaskArgs_AllArgs_PayloadContent(self):
    expected_config = _MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = (
        _MESSAGES_MODULE.AppEngineHttpRequest.HttpMethodValueValuesEnum(
            'POST'))
    expected_config.appEngineHttpRequest = (
        _MESSAGES_MODULE.AppEngineHttpRequest(
            appEngineRouting=_MESSAGES_MODULE.AppEngineRouting(service='abc'),
            headers=encoding.DictToAdditionalPropertyMessage(
                {'header1': 'value1', 'header2': 'value2'},
                _MESSAGES_MODULE.AppEngineHttpRequest.HeadersValue),
            httpMethod=http_method, body=b'body',
            relativeUri='/paths/a/'))
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time), '--body-content=body',
        '--method=POST', 'my-task', '--queue=queue_name',
        '--relative-uri=/paths/a/', '--header=header1:value1',
        '--header=header2:value2', '--routing=service:abc'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.APP_ENGINE_TASK, _MESSAGES_MODULE)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_AllArgs_PayloadFile(self):
    expected_config = _MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = (
        _MESSAGES_MODULE.AppEngineHttpRequest.HttpMethodValueValuesEnum(
            'POST'))
    expected_config.appEngineHttpRequest = (
        _MESSAGES_MODULE.AppEngineHttpRequest(
            appEngineRouting=_MESSAGES_MODULE.AppEngineRouting(service='abc'),
            headers=encoding.DictToAdditionalPropertyMessage(
                {'header1': 'value1', 'header2': 'value2'},
                _MESSAGES_MODULE.AppEngineHttpRequest.HeadersValue),
            httpMethod=http_method, body=b'body',
            relativeUri='/paths/a/'))
    self.Touch(self.temp_path, 'body.txt', contents='body')
    payload_file = os.path.join(self.temp_path, 'body.txt')
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time),
        '--body-file={}'.format(payload_file), '--method=POST', 'my-task',
        '--queue=queue_id', '--relative-uri=/paths/a/',
        '--header=header1:value1', '--header=header2:value2',
        '--routing=service:abc'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.APP_ENGINE_TASK, _MESSAGES_MODULE)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_RepeatedHeadersKey(self):
    expected_config = _MESSAGES_MODULE.Task()
    expected_config.appEngineHttpRequest = (
        _MESSAGES_MODULE.AppEngineHttpRequest(
            headers=encoding.DictToAdditionalPropertyMessage(
                {'header': 'value2'},
                _MESSAGES_MODULE.AppEngineHttpRequest.HeadersValue)))
    args = self.parser.parse_args([
        'my-task', '--queue=queue_id', '--header=header:value1',
        '--header=header:value2'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.APP_ENGINE_TASK, _MESSAGES_MODULE)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_IncludePullArgs(self):
    with self.AssertRaisesArgumentErrorMatches('unrecognized arguments:'):
      self.parser.parse_args([
          '--schedule-time={}'.format(self.schedule_time), '--tag=tag',
          '--body-content=body', '--method=POST', '--queue=queue_id',
          '--relative-uri=/paths/a/', '--header=header1:value1',
          '--header=header2:value2', '--routing=service:abc'
      ])

  def testAppEngineRoutingKeyValidator(self):
    with self.AssertRaisesArgumentErrorMatches(
        'Only the following keys are valid for routing'):
      self.parser.parse_args(['--routing=target:abc'])

  def testHeaderArgValidator(self):
    with self.AssertRaisesArgumentErrorMatches(
        'Must be of the form: "HEADER_FIELD: HEADER_VALUE'):
      self.parser.parse_args(['--header="target=abc"'])


class ParseHttpTaskArgsTest(ParseArgsTestBase):

  def SetUp(self):
    flags.AddCreateHttpTaskFlags(self.parser)
    self.schedule_time = time_util.CalculateExpiration(20)

  def testParseCreateTaskArgs_NoArgs(self):
    with self.AssertRaisesArgumentErrorMatches(
        'argument --queue --url: Must be specified.'):
      self.parser.parse_args([])

  def testParseCreateTaskArgs_AllArgs_PayloadContent(self):
    expected_config = _BETA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = _BETA_MESSAGES_MODULE.HttpRequest.HttpMethodValueValuesEnum(
        'POST')
    expected_config.httpRequest = (
        _BETA_MESSAGES_MODULE.HttpRequest(
            headers=encoding.DictToAdditionalPropertyMessage(
                {'header1': 'value1', 'header2': 'value2'},
                _BETA_MESSAGES_MODULE.HttpRequest.HeadersValue),
            httpMethod=http_method, body=b'body',
            url='http://somehost.com/paths/a/'))
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time), '--body-content=body',
        '--method=POST', 'my-task', '--queue=queue_name',
        '--url=http://somehost.com/paths/a/', '--header=header1:value1',
        '--header=header2:value2'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.HTTP_TASK, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_AllArgs_PayloadFile(self):
    expected_config = _BETA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = _BETA_MESSAGES_MODULE.HttpRequest.HttpMethodValueValuesEnum(
        'POST')
    expected_config.httpRequest = (
        _BETA_MESSAGES_MODULE.HttpRequest(
            headers=encoding.DictToAdditionalPropertyMessage(
                {'header1': 'value1', 'header2': 'value2'},
                _BETA_MESSAGES_MODULE.HttpRequest.HeadersValue),
            httpMethod=http_method, body=b'body',
            url='http://somehost.com/paths/a/'))
    self.Touch(self.temp_path, 'body.txt', contents='body')
    payload_file = os.path.join(self.temp_path, 'body.txt')
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time),
        '--body-file={}'.format(payload_file), '--method=POST', 'my-task',
        '--queue=queue_id', '--url=http://somehost.com/paths/a/',
        '--header=header1:value1', '--header=header2:value2',
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.HTTP_TASK, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_RepeatedHeadersKey(self):
    expected_config = _BETA_MESSAGES_MODULE.Task()
    expected_config.httpRequest = (
        _BETA_MESSAGES_MODULE.HttpRequest(
            headers=encoding.DictToAdditionalPropertyMessage(
                {'header': 'value2'},
                _BETA_MESSAGES_MODULE.HttpRequest.HeadersValue),
            url='http://somehost.com/paths/a/'))
    args = self.parser.parse_args([
        'my-task', '--queue=queue_id', '--header=header:value1',
        '--header=header:value2', '--url=http://somehost.com/paths/a/'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.HTTP_TASK, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_Oidc(self):
    expected_config = _BETA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = _BETA_MESSAGES_MODULE.HttpRequest.HttpMethodValueValuesEnum(
        'POST')
    expected_config.httpRequest = (
        _BETA_MESSAGES_MODULE.HttpRequest(
            httpMethod=http_method,
            url='http://somehost.com/paths/a/',
            oidcToken=_BETA_MESSAGES_MODULE.OidcToken(
                serviceAccountEmail='some.email@org.com',
                audience='some-audience')))
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time),
        '--method=POST', 'my-task', '--queue=queue_name',
        '--url=http://somehost.com/paths/a/',
        '--oidc-service-account-email=some.email@org.com',
        '--oidc-token-audience=some-audience'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.HTTP_TASK, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_OidcServiceAccountOnly(self):
    expected_config = _BETA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = _BETA_MESSAGES_MODULE.HttpRequest.HttpMethodValueValuesEnum(
        'POST')
    expected_config.httpRequest = (
        _BETA_MESSAGES_MODULE.HttpRequest(
            httpMethod=http_method,
            url='http://somehost.com/paths/a/',
            oidcToken=_BETA_MESSAGES_MODULE.OidcToken(
                serviceAccountEmail='some.email@org.com')))
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time),
        '--method=POST', 'my-task', '--queue=queue_name',
        '--url=http://somehost.com/paths/a/',
        '--oidc-service-account-email=some.email@org.com'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.HTTP_TASK, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_OAuth(self):
    expected_config = _BETA_MESSAGES_MODULE.Task()
    schedule_time = self.schedule_time
    expected_config.scheduleTime = schedule_time
    http_method = _BETA_MESSAGES_MODULE.HttpRequest.HttpMethodValueValuesEnum(
        'POST')
    expected_config.httpRequest = (
        _BETA_MESSAGES_MODULE.HttpRequest(
            httpMethod=http_method,
            url='http://somehost.com/paths/a/',
            oauthToken=_BETA_MESSAGES_MODULE.OAuthToken(
                serviceAccountEmail='some.email@org.com',
                scope='some-scope')))
    args = self.parser.parse_args([
        '--schedule-time={}'.format(schedule_time),
        '--method=POST', 'my-task', '--queue=queue_name',
        '--url=http://somehost.com/paths/a/',
        '--oauth-service-account-email=some.email@org.com',
        '--oauth-token-scope=some-scope'
    ])
    actual_config = parsers.ParseCreateTaskArgs(
        args, constants.HTTP_TASK, _BETA_MESSAGES_MODULE,
        release_track=base.ReleaseTrack.BETA)
    self.assertEqual(actual_config, expected_config)

  def testParseCreateTaskArgs_BothOidcAndOAuth(self):
    with self.AssertRaisesArgumentErrorMatches('At most one of'):
      self.parser.parse_args([
          '--schedule-time={}'.format(self.schedule_time),
          '--method=POST', 'my-task', '--queue=queue_name',
          '--url=http://somehost.com/paths/a/',
          '--oidc-service-account-email=some.email@org.com',
          '--oauth-service-account-email=some.email@org.com'
      ])

  def testParseCreateTaskArgs_IncludePullArgs(self):
    with self.AssertRaisesArgumentErrorMatches('unrecognized arguments:'):
      self.parser.parse_args([
          '--schedule-time={}'.format(self.schedule_time), '--tag=tag',
          '--body-content=body', '--method=POST', '--queue=queue_id',
          '--url=http://somehost.com/paths/a/', '--header=header1:value1',
          '--header=header2:value2'
      ])

  def testParseCreateTaskArgs_IncludeAppEngineArgs(self):
    with self.AssertRaisesArgumentErrorMatches('unrecognized arguments:'):
      self.parser.parse_args([
          '--schedule-time={}'.format(self.schedule_time),
          '--body-content=body', '--method=POST', '--queue=queue_id',
          '--url=http://somehost.com/paths/a/', '--header=header1:value1',
          '--header=header2:value2', '--routing=service:abc'
      ])

  def testHeaderArgValidator(self):
    with self.AssertRaisesArgumentErrorMatches(
        'Must be of the form: "HEADER_FIELD: HEADER_VALUE'):
      self.parser.parse_args(['--header="target=abc"'])


if __name__ == '__main__':
  test_case.main()
