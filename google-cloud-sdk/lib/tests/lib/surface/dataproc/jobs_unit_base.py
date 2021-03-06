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

"""Test of the 'jobs' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections
import copy

from apitools.base.py import encoding

from googlecloudsdk.api_lib.dataproc import storage_helpers
from googlecloudsdk.api_lib.dataproc import util
from tests.lib.surface.dataproc import unit_base
import six


class _FakeJobStream(object):
  """Very naive fake job stream."""

  LINES = [
      'First line of job output.\n',
      'Next line of job output.\n',
      'Yet another line of job output.\n',
      'Last line of job output.\n',
  ]

  def __init__(self, lines=None):
    self._lines = copy.copy(lines or self.LINES)

  @property
  def open(self):
    return bool(self._lines)

  # pylint: disable=invalid-name
  def ReadIntoWritable(self, stream):
    line = self._lines.pop(0)
    stream.write(line)
    return len(line)


class JobsUnitTestBase(unit_base.DataprocUnitTestBase):
  """Tests for dataproc jobs commands."""

  JOB_ID = 'dbf5f287-f332-470b-80b2-c94b49358c45'
  JOB_IDS = [
      'dbf2d1b1-c14e-4f78-8d05-cfdb48b51a66',
      'a0aa06f9-41b7-48f3-9694-18e31bb78685',
      '90471700-f11d-413a-8d60-012ba3de4aee']

  CLASS = 'com.google.cloud.hadoop.test.FooBar'
  JOB_ARGS = ['foo', '--bar', 'baz']

  SCRIPT_URI = 'gs://test-bucket/test/path/foo.script'
  R_SCRIPT_URI = 'gs://test-bucket/test/path/foo.R'
  DRIVER_URI = 'gs://test-bucket/test/path/driveroutput'
  JAR_URIS = [
      'gs://test-bucket/test/path/jar1',
      'gs://test-bucket/test/path/jar2'
  ]
  JAR_URI = JAR_URIS[0]
  ARCHIVE_URIS = ['gs://bucket/archive1.zip', 'gs://bucket/archive2.zip']
  FILE_URIS = ['gs://bucket/object1', 'gs://bucket/object2']
  PYFILE_URIS = ['gs://bucket/file1.py', 'gs://bucket/file2.py']
  PRESTO_OUTPUT_FORMAT = 'foo-output'
  PRESTO_CLIENT_TAGS = ['foo-tag', 'bar-tag']

  PARAMS = collections.OrderedDict([
      ('foo', 'bar'),
      ('var', 'value')])

  PROPERTIES = collections.OrderedDict([
      ('foo', 'bar'),
      ('some.key', 'some.value')])

  SECOND_ATTEMPT_JOB_OUTPUT_LINES = [
      "Oops let's try that again.\n"
      'This time for sure.\n'
  ]

  THIRD_ATTEMPT_JOB_OUTPUT_LINES = [
      'Why is this happening?!?\n'
      'All done :D\n'
  ]

  STEP_ID = '001'
  PREREQUISITE_STEP_IDS = ['001']

  QUERY = 'GROUPS = GROUP WORDS BY word'

  @property
  def STATE_ENUM(self):
    return self.messages.JobStatus.StateValueValuesEnum

  @property
  def LOG_CONFIG(self):
    value_enum = (self.messages.LoggingConfig.DriverLogLevelsValue.
                  AdditionalProperty.ValueValueValuesEnum)
    return self.messages.LoggingConfig(
        driverLogLevels=encoding.DictToAdditionalPropertyMessage(
            collections.OrderedDict([
                ('root', value_enum.INFO),
                ('com.example', value_enum.DEBUG)]),
            self.messages.LoggingConfig.DriverLogLevelsValue))

  @property
  def HADOOP_JOB(self):
    return self.messages.HadoopJob(
        mainClass=self.CLASS,
        args=self.JOB_ARGS,
        loggingConfig=self.LOG_CONFIG,
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.HadoopJob.PropertiesValue))

  @property
  def SPARK_JOB(self):
    return self.messages.SparkJob(
        mainClass=self.CLASS,
        args=self.JOB_ARGS,
        loggingConfig=self.LOG_CONFIG,
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.SparkJob.PropertiesValue))

  @property
  def PYSPARK_JOB(self):
    return self.messages.PySparkJob(
        mainPythonFileUri=self.SCRIPT_URI,
        args=self.JOB_ARGS,
        jarFileUris=self.JAR_URIS,
        loggingConfig=self.LOG_CONFIG,
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.PySparkJob.PropertiesValue))

  @property
  def HIVE_JOB(self):
    return self.messages.HiveJob(
        continueOnFailure=False,
        queryFileUri=self.SCRIPT_URI,
        scriptVariables=encoding.DictToAdditionalPropertyMessage(
            self.PARAMS, self.messages.HiveJob.ScriptVariablesValue),
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.HiveJob.PropertiesValue))

  @property
  def SPARK_SQL_JOB(self):
    return self.messages.SparkSqlJob(
        queryFileUri=self.SCRIPT_URI,
        loggingConfig=self.LOG_CONFIG,
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.SparkSqlJob.PropertiesValue))

  @property
  def PIG_JOB(self):
    return self.messages.PigJob(
        continueOnFailure=False,
        queryFileUri=self.SCRIPT_URI,
        loggingConfig=self.LOG_CONFIG,
        scriptVariables=encoding.DictToAdditionalPropertyMessage(
            self.PARAMS, self.messages.PigJob.ScriptVariablesValue),
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.PigJob.PropertiesValue))

  @property
  def SPARK_R_JOB(self):
    return self.messages.SparkRJob(
        mainRFileUri=self.R_SCRIPT_URI,
        args=self.JOB_ARGS,
        loggingConfig=self.LOG_CONFIG,
        properties=encoding.DictToMessage(
            self.PROPERTIES, self.messages.SparkRJob.PropertiesValue))

  @property
  def PRESTO_JOB(self):
    return self.messages.PrestoJob(
        continueOnFailure=False,
        queryFileUri=self.SCRIPT_URI,
        loggingConfig=self.LOG_CONFIG,
        outputFormat=self.PRESTO_OUTPUT_FORMAT,
        clientTags=self.PRESTO_CLIENT_TAGS,
        properties=encoding.DictToAdditionalPropertyMessage(
            self.PROPERTIES, self.messages.PrestoJob.PropertiesValue))

  def SetUp(self):
    # Set 0s sleep intervals in waiters.
    real_wait = util.WaitForJobTermination

    def NoSleep(*args, **kwargs):
      if not kwargs:
        kwargs = {}
      kwargs.update({'log_poll_period_s': 0, 'dataproc_poll_period_s': 0})
      return real_wait(*args, **kwargs)
    self.StartObjectPatch(util, 'WaitForJobTermination').side_effect = NoSleep

    self.mock_upload = self.StartObjectPatch(storage_helpers, 'Upload')
    self.StartObjectPatch(
        storage_helpers,
        'StorageObjectSeriesStream',
        side_effect=[
            _FakeJobStream(),
            _FakeJobStream(self.SECOND_ATTEMPT_JOB_OUTPUT_LINES),
            _FakeJobStream(self.THIRD_ATTEMPT_JOB_OUTPUT_LINES),
        ])

  def MakeJob(self, **kwargs):
    job = self.messages.Job(
        reference=self.messages.JobReference(
            jobId=kwargs.get('jobId', self.JOB_ID),
            projectId=kwargs.get('projectId', self.Project())),
        placement=self.messages.JobPlacement(
            clusterName=kwargs.get('clusterName', self.CLUSTER_NAME)),
        status=(None if 'state' not in kwargs else self.messages.JobStatus(
            state=kwargs['state'])),
        driverOutputResourceUri=kwargs.get('driverOutputResourceUri', None))
    job_type_keys = [key for key in kwargs.keys() if key.endswith('Job')]
    if job_type_keys:
      for job_type in job_type_keys:
        setattr(job, job_type, kwargs[job_type])
    else:
      job.hadoopJob = self.HADOOP_JOB

    # Convert from a dict to Python client library version of dict (LabelsValue)
    labels = kwargs.get('labels', None)
    if labels is not None:
      job.labels = self.ConvertLabels(labels)

    return job

  def MakeSubmittedJob(self, **kwargs):
    kwargs.update({'state': self.STATE_ENUM.PENDING})
    return self.MakeJob(**kwargs)

  def MakeRunningJob(self, **kwargs):
    kwargs.update({
        'state': self.STATE_ENUM.RUNNING,
        'driverOutputResourceUri': self.DRIVER_URI})
    return self.MakeJob(**kwargs)

  def MakeCompletedJob(self, **kwargs):
    kwargs.update({
        'state': self.STATE_ENUM.DONE,
        'driverOutputResourceUri': self.DRIVER_URI})
    return self.MakeJob(**kwargs)

  def ExpectGetJob(self, job=None, response=None, exception=None, region=None):
    if not job:
      job = self.MakeRunningJob()
    if region is None:
      region = self.REGION
    if not (response or exception):
      response = copy.deepcopy(job)
    self.mock_client.projects_regions_jobs.Get.Expect(
        self.messages.DataprocProjectsRegionsJobsGetRequest(
            region=region,
            jobId=job.reference.jobId,
            projectId=self.Project()),
        response=response,
        exception=exception)
    return response

  def ExpectSubmitJob(
      self, job=None, response=None, exception=None, region=None):
    if not job:
      job = self.MakeJob()
    if region is None:
      region = self.REGION
    if not (response or exception):
      response = copy.deepcopy(job)
      response.status = self.messages.JobStatus(state=self.STATE_ENUM.PENDING)
    self.mock_client.projects_regions_jobs.Submit.Expect(
        self.messages.DataprocProjectsRegionsJobsSubmitRequest(
            region=region,
            projectId=self.Project(),
            submitJobRequest=self.messages.SubmitJobRequest(
                job=job,
                requestId=self.REQUEST_ID)),
        response=response,
        exception=exception)
    return response

  def ExpectWaitCalls(
      self, job=None, final_state=None, details=None, region=None):
    if not job:
      job = self.MakeSubmittedJob()
    if region is None:
      region = self.REGION
    if not final_state:
      final_state = self.STATE_ENUM.DONE
    self.ExpectGetJob(job=job, region=region)
    self.ExpectGetJob(job=job, region=region)
    job = copy.deepcopy(job)
    job.driverOutputResourceUri = self.DRIVER_URI
    job.status.state = self.STATE_ENUM.RUNNING
    self.ExpectGetJob(job=job, region=region)
    self.ExpectGetJob(job=job, region=region)
    job = copy.deepcopy(job)
    job.status.state = final_state
    job.status.details = details
    self.ExpectGetJob(job=job, region=region)
    return job

  def ExpectSubmitCalls(self, job=None, **kwargs):
    if not job:
      job = self.MakeJob()
    self.ExpectGetCluster()
    job = self.ExpectSubmitJob(job=job)
    return self.ExpectWaitCalls(job=job, **kwargs)

  def ExpectUpdateWorkflowTemplatesJobCalls(self,
                                            workflow_template=None,
                                            ordered_jobs=None,
                                            response=None,
                                            exception=None):
    if not workflow_template:
      workflow_template = self.MakeWorkflowTemplate()
    self.ExpectGetWorkflowTemplate(
        name=workflow_template.name,
        version=workflow_template.version,
        response=workflow_template)
    if ordered_jobs is None:
      ordered_jobs = [self.MakeOrderedJob()]
    new_template = copy.deepcopy(workflow_template)
    new_template.jobs = ordered_jobs
    if not (response or exception):
      response = copy.deepcopy(new_template)
    self.mock_client.projects_regions_workflowTemplates.Update.Expect(
        new_template, response=response, exception=exception)
    return response

  def ConvertLabels(self, labels):
    # Convert labels from Python dict to client library dict
    return self.messages.Job.LabelsValue(additionalProperties=[
        self.messages.Job.LabelsValue.AdditionalProperty(key=key, value=value)
        for key, value in sorted(six.iteritems(labels))
    ])

  def ConvertOrderedJobLabels(self, labels):
    # Convert labels from Python dict to client library dict
    return self.messages.OrderedJob.LabelsValue(additionalProperties=[
        self.messages.OrderedJob.LabelsValue.AdditionalProperty(
            key=key, value=value)
        for key, value in sorted(six.iteritems(labels))
    ])

  def MakeOrderedJob(self, **kwargs):
    """Create a mock OrderedJob.

    Args:
      **kwargs: args contain step_id, start_after, labels, and a Job class for
        the OrderedJob.

    Returns:
      An instance of OrderedJob.

    """
    job = self.messages.OrderedJob(stepId=kwargs.get('step_id', self.STEP_ID))
    start_after = kwargs.get('start_after', None)
    if start_after:
      job.prerequisiteStepIds = start_after
    job_type_keys = [key for key in kwargs.keys() if key.endswith('Job')]
    if job_type_keys:
      for job_type in job_type_keys:
        setattr(job, job_type, kwargs[job_type])
    else:
      job.hadoopJob = self.HADOOP_JOB

    # Convert from a dict to Python client library version of dict (LabelsValue)
    labels = kwargs.get('labels', None)
    if labels:
      test = self.ConvertOrderedJobLabels(labels)
      job.labels = test

    return job
