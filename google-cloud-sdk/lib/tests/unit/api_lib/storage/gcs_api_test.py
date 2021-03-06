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
"""Tests for googlecloudsdk.api_lib.storage.storage_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from apitools.base.py import list_pager
from apitools.base.py import transfer as apitools_transfer

from googlecloudsdk.api_lib.storage import cloud_api
from googlecloudsdk.api_lib.storage import errors as cloud_errors
from googlecloudsdk.api_lib.storage import gcs_api
from googlecloudsdk.api_lib.util import apis as core_apis
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.command_lib.storage.resources import gcs_resource_reference
from googlecloudsdk.command_lib.storage.resources import resource_reference
from googlecloudsdk.core import properties
from tests.lib import parameterized
from tests.lib import sdk_test_base
from tests.lib import test_case
from tests.lib.surface.app import cloud_storage_util
from tests.lib.surface.storage import test_resources

import mock


TEST_ACCOUNT = 'fake-account'
TEST_BUCKET = 'fake-bucket'
TEST_OBJECT = 'fake-object'
TEST_PROJECT = 'fake-project'


@test_case.Filters.DoNotRunOnPy2('Storage does not support Python 2.')
class CreateBucketTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                       sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageBucketsInsertRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_create_bucket(self):
    bucket_metadata = self.messages.Bucket(name=TEST_BUCKET)
    self.apitools_client.buckets.Insert.Expect(
        self.messages.StorageBucketsInsertRequest(
            bucket=bucket_metadata, project=TEST_PROJECT,
            projection=self.default_projection),
        response=bucket_metadata)

    expected_resource = gcs_api._bucket_resource_from_metadata(bucket_metadata)
    observed_resource = self.gcs_client.create_bucket(expected_resource)
    self.assertEqual(observed_resource, expected_resource)

  def test_creates_missing_bucket_metadata(self):
    expected_metadata = self.messages.Bucket(name='b')
    self.apitools_client.buckets.Insert.Expect(
        self.messages.StorageBucketsInsertRequest(
            bucket=expected_metadata, project=TEST_PROJECT,
            projection=self.default_projection),
        response=expected_metadata)

    expected_resource = gcs_api._bucket_resource_from_metadata(
        expected_metadata)
    observed_resource = self.gcs_client.create_bucket(
        test_resources.from_url_string('gs://b'))
    self.assertEqual(observed_resource, expected_resource)

  def test_create_bucket_api_error(self):
    bucket_metadata = self.messages.Bucket(name=TEST_BUCKET)
    self.apitools_client.buckets.Insert.Expect(
        self.messages.StorageBucketsInsertRequest(
            bucket=bucket_metadata, project=TEST_PROJECT,
            projection=self.default_projection),
        exception=apitools_exceptions.HttpError(None, None, None))
    bucket_resource = gcs_api._bucket_resource_from_metadata(bucket_metadata)

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.create_bucket(bucket_resource)

  def test_create_bucket_invalid_fields_scope(self):
    bucket_metadata = self.messages.Bucket(name=TEST_BUCKET)
    bucket_resource = gcs_api._bucket_resource_from_metadata(bucket_metadata)
    with self.assertRaises(ValueError):
      self.gcs_client.create_bucket(
          bucket_resource, fields_scope='football field')

  @parameterized.parameters(
      (cloud_api.FieldsScope.SHORT, 'noAcl'),
      (cloud_api.FieldsScope.NO_ACL, 'noAcl'),
      (cloud_api.FieldsScope.FULL, 'full'))
  def test_create_bucket_valid_fields_scope(self, fields_scope, projection):
    bucket_metadata = self.messages.Bucket(name=TEST_BUCKET)
    request = self.messages.StorageBucketsInsertRequest(
        bucket=bucket_metadata,
        project=TEST_PROJECT,
        projection=getattr(self.messages.StorageBucketsInsertRequest
                           .ProjectionValueValuesEnum, projection))
    bucket_resource = gcs_api._bucket_resource_from_metadata(bucket_metadata)

    with mock.patch.object(self.apitools_client.buckets,
                           'Insert') as mock_insert:
      self.gcs_client.create_bucket(bucket_resource, fields_scope=fields_scope)
      mock_insert.assert_called_once_with(request)


class DeleteBucketTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                       sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.gcs_client = gcs_api.GcsApi()

  def test_delete_bucket(self):
    self.apitools_client.buckets.Delete.Expect(
        self.messages.StorageBucketsDeleteRequest(bucket=TEST_BUCKET),
        response=self.messages.StorageBucketsDeleteResponse())

    self.gcs_client.delete_bucket(TEST_BUCKET)

  def test_delete_bucket_api_error(self):
    self.apitools_client.buckets.Delete.Expect(
        self.messages.StorageBucketsDeleteRequest(bucket=TEST_BUCKET),
        exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.delete_bucket(TEST_BUCKET)

  def test_delete_bucket_precondition_metageneration_match(self):
    precondition_metageneration_match = 1
    self.apitools_client.buckets.Delete.Expect(
        self.messages.StorageBucketsDeleteRequest(
            bucket=TEST_BUCKET,
            ifMetagenerationMatch=precondition_metageneration_match),
        response=self.messages.StorageBucketsDeleteResponse())

    request_config = gcs_api.GcsRequestConfig(
        precondition_metageneration_match=precondition_metageneration_match)
    self.gcs_client.delete_bucket(TEST_BUCKET, request_config)


class GetBucketTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                    sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageBucketsGetRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_get_bucket(self):
    self.apitools_client.buckets.Get.Expect(
        self.messages.StorageBucketsGetRequest(
            bucket=TEST_BUCKET, projection=self.default_projection),
        response=self.messages.Bucket())

    self.gcs_client.get_bucket(TEST_BUCKET)

  def test_get_bucket_api_error(self):
    self.apitools_client.buckets.Get.Expect(
        self.messages.StorageBucketsGetRequest(
            bucket=TEST_BUCKET, projection=self.default_projection),
        exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.get_bucket(TEST_BUCKET)

  def test_get_bucket_invalid_fields_scope(self):
    with self.assertRaises(ValueError):
      self.gcs_client.get_bucket(TEST_BUCKET, fields_scope='football field')

  @parameterized.parameters(
      (cloud_api.FieldsScope.SHORT, 'noAcl'),
      (cloud_api.FieldsScope.NO_ACL, 'noAcl'),
      (cloud_api.FieldsScope.FULL, 'full'))
  def test_get_bucket_valid_fields_scope(self, fields_scope, projection):
    request = self.messages.StorageBucketsGetRequest(
        bucket=TEST_BUCKET,
        projection=getattr(self.messages.StorageBucketsGetRequest
                           .ProjectionValueValuesEnum, projection))

    with mock.patch.object(self.apitools_client.buckets, 'Get') as mock_get:
      self.gcs_client.get_bucket(TEST_BUCKET, fields_scope=fields_scope)
      mock_get.assert_called_once_with(request)


class ListBucketsTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                      sdk_test_base.SdkBase):

  _BUCKET_NAMES = ['Bucket1', 'Bucket2', 'Bucket3']

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageBucketsListRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_list_buckets(self):
    buckets = [self.messages.Bucket(name=name)
               for name in self._BUCKET_NAMES]
    self.apitools_client.buckets.List.Expect(
        self.messages.StorageBucketsListRequest(
            project=TEST_PROJECT, projection=self.default_projection),
        response=self.messages.Buckets(items=buckets))

    names = [b.metadata.name for b in self.gcs_client.list_buckets()]
    self.assertCountEqual(names, self._BUCKET_NAMES)

  def test_list_buckets_api_error(self):
    self.apitools_client.buckets.List.Expect(
        self.messages.StorageBucketsListRequest(
            project=TEST_PROJECT, projection=self.default_projection),
        exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      list(self.gcs_client.list_buckets())

  def test_list_buckets_invalid_fields_scope(self):
    with self.assertRaises(ValueError):
      list(self.gcs_client.list_buckets(fields_scope='football field'))

  @parameterized.parameters(
      (cloud_api.FieldsScope.SHORT, 'noAcl', 'items/name'),
      (cloud_api.FieldsScope.NO_ACL, 'noAcl', None),
      (cloud_api.FieldsScope.FULL, 'full', None))
  def test_list_buckets_valid_fields_scope(self, fields_scope, projection,
                                           fields):

    request = self.messages.StorageBucketsListRequest(
        project=TEST_PROJECT,
        projection=getattr(self.messages.StorageBucketsListRequest
                           .ProjectionValueValuesEnum, projection))

    global_params = None
    if fields:
      global_params = self.messages.StandardQueryParameters()
      global_params.fields = fields

    with mock.patch.object(list_pager, 'YieldFromList') as mock_yield_from_list:
      list(self.gcs_client.list_buckets(fields_scope))

      # Checks for correct projection value inside request.
      # Checks for correct fields value inside global_params.
      mock_yield_from_list.assert_called_once_with(
          self.apitools_client.buckets,
          request,
          batch_size=cloud_api.NUM_ITEMS_PER_LIST_PAGE,
          global_params=global_params)


@test_case.Filters.DoNotRunOnPy2('Storage does not support Python 2.')
class ListObjectsTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                      sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageObjectsListRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_list_objects(self):
    file_list = ['content', 'content', 'content2']
    objects = self.messages.Objects(
        items=[self.messages.Object(name=c) for c in file_list])

    self.apitools_client.objects.List.Expect(
        self.messages.StorageObjectsListRequest(
            bucket=TEST_BUCKET,
            projection=self.default_projection),
        response=objects
    )

    names = [o.name for o in self.gcs_client.list_objects(TEST_BUCKET)]
    self.assertCountEqual(names, file_list)

  def test_list_objects_api_error(self):
    self.apitools_client.objects.List.Expect(
        self.messages.StorageObjectsListRequest(
            bucket=TEST_BUCKET,
            projection=self.default_projection),
        exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      list(self.gcs_client.list_objects(TEST_BUCKET))

  def test_list_objects_invalid_fields_scope(self):
    with self.assertRaises(ValueError):
      list(
          self.gcs_client.list_objects(
              TEST_BUCKET, fields_scope='football field'))

  def test_list_objects_and_prefixes(self):
    file_list = ['obj1', 'obj2', 'obj3']
    prefixes = ['prefix1', 'prefix2']
    objects = self.messages.Objects(
        items=[self.messages.Object(name=c) for c in file_list],
        prefixes=prefixes)

    self.apitools_client.objects.List.Expect(
        self.messages.StorageObjectsListRequest(
            bucket=TEST_BUCKET,
            projection=self.default_projection),
        response=objects
    )

    object_names = []
    prefixes_names = []

    for resource in self.gcs_client.list_objects(TEST_BUCKET):
      if isinstance(resource, gcs_resource_reference.GcsObjectResource):
        object_names.append(resource.name)
      elif isinstance(resource, resource_reference.PrefixResource):
        prefixes_names.append(resource.prefix)
      else:
        self.fail('Invalid resource found.')

    self.assertCountEqual(object_names, file_list)
    self.assertCountEqual(prefixes_names, prefixes)


@test_case.Filters.DoNotRunOnPy2('Storage does not support Python 2.')
class ListObjectsWithoutApitoolsMockTest(parameterized.TestCase,
                                         sdk_test_base.SdkBase):
  """Test class to test list_objects without using apitools.mock.

  apitools_client.objects.List.Expect does work for testing global_params or
  for cases where we make multiple API calls. Hence, instead of relying on
  apitools.mock, we will mock api client directly in each test case.
  """

  def SetUp(self):
    self.messages = core_apis.GetMessagesModule('storage', 'v1')

  @parameterized.parameters(
      (cloud_api.FieldsScope.SHORT, 'noAcl',
       'prefixes,items/name,items/size,items/generation'),
      (cloud_api.FieldsScope.NO_ACL, 'noAcl', None),
      (cloud_api.FieldsScope.FULL, 'full', None))
  def test_list_objects_valid_fields_scope(self, fields_scope,
                                           projection, fields):
    list_object_response = self.messages.Objects(items=[
        self.messages.Object(name='object1'),
        self.messages.Object(name='object2'),
    ])
    api_client = mock.MagicMock(spec=['objects'])
    api_client.objects.List.return_value = list_object_response
    expected_request = self.messages.StorageObjectsListRequest(
        bucket=TEST_BUCKET,
        projection=getattr(
            self.messages.StorageObjectsListRequest.ProjectionValueValuesEnum,
            projection
        ),
        maxResults=cloud_api.NUM_ITEMS_PER_LIST_PAGE
    )
    global_params = None
    if fields:
      global_params = self.messages.StandardQueryParameters()
      global_params.fields = fields

    with mock.patch.object(core_apis, 'GetClientInstance', autospec=True,
                           return_value=api_client) as mock_get_instance:
      gcs_client = gcs_api.GcsApi()
      list(gcs_client.list_objects(TEST_BUCKET, fields_scope=fields_scope))

      mock_get_instance.assert_called_once_with('storage', 'v1')
      api_client.objects.List.assert_called_once_with(
          expected_request,
          global_params=global_params)

  @mock.patch.object(gcs_api.cloud_api, 'NUM_ITEMS_PER_LIST_PAGE', 3)
  @mock.patch.object(core_apis, 'GetClientInstance', autospec=True)
  def test_list_objects_paging(self, mock_get_instance):
    filenames_batch1 = ['obj1', 'obj2', 'obj3']
    filenames_batch2 = ['obj4', 'obj5', 'obj6']
    filenames_batch3 = ['obj7']
    list_objects_response = [
        self.messages.Objects(
            items=[self.messages.Object(name=c) for c in filenames_batch1],
            nextPageToken='page2'
        ),
        self.messages.Objects(
            items=[self.messages.Object(name=c) for c in filenames_batch2],
            nextPageToken='page3'
        ),
        self.messages.Objects(
            items=[self.messages.Object(name=c) for c in filenames_batch3]
        )
    ]

    default_projection = (self.messages.StorageObjectsListRequest
                          .ProjectionValueValuesEnum.noAcl)

    mock_api_client = mock.MagicMock(spec=['objects'])
    # "If side_effect is an iterable then each call to the mock will return
    # the next value from the iterable."
    # https://docs.python.org/3/library/unittest.mock.html#the-mock-class
    mock_api_client.objects.List.side_effect = list_objects_response
    mock_get_instance.return_value = mock_api_client

    gcs_client = gcs_api.GcsApi()
    mock_get_instance.assert_called_once_with('storage', 'v1')

    objects = list(gcs_client.list_objects(TEST_BUCKET))

    # Check that we looped over all the objects.
    self.assertCountEqual(
        [o.name for o in objects],
        filenames_batch1 + filenames_batch2 + filenames_batch3
    )

    # Check if calls to List are made as expected. We expected 3 calls.
    expected_list_object_calls = []
    for page_token in (None, 'page2', 'page3'):
      expected_call = mock.call(
          self.messages.StorageObjectsListRequest(
              bucket=TEST_BUCKET,
              projection=default_projection,
              pageToken=page_token,
              maxResults=3),
          global_params=None
      )
      expected_list_object_calls.append(expected_call)

    self.assertCountEqual(mock_api_client.objects.List.mock_calls,
                          expected_list_object_calls)


class DeleteObjectTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                       sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.gcs_client = gcs_api.GcsApi()

  def test_delete_object(self):
    self.apitools_client.objects.Delete.Expect(
        self.messages.StorageObjectsDeleteRequest(bucket=TEST_BUCKET,
                                                  object=TEST_OBJECT),
        response=self.messages.StorageObjectsDeleteResponse())

    self.gcs_client.delete_object(TEST_BUCKET, TEST_OBJECT)

  def test_delete_object_api_error(self):
    self.apitools_client.objects.Delete.Expect(
        self.messages.StorageObjectsDeleteRequest(bucket=TEST_BUCKET,
                                                  object=TEST_OBJECT),
        exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.delete_object(TEST_BUCKET, TEST_OBJECT)

  def test_delete_object_generation(self):
    generation = 1
    self.apitools_client.objects.Delete.Expect(
        self.messages.StorageObjectsDeleteRequest(
            bucket=TEST_BUCKET,
            object=TEST_OBJECT,
            generation=generation),
        response=self.messages.StorageObjectsDeleteResponse())

    self.gcs_client.delete_object(
        TEST_BUCKET, TEST_OBJECT, generation=generation)

  def test_delete_object_precondition_generation_match(self):
    precondition_generation_match = 1
    self.apitools_client.objects.Delete.Expect(
        self.messages.StorageObjectsDeleteRequest(
            bucket=TEST_BUCKET,
            object=TEST_OBJECT,
            ifGenerationMatch=precondition_generation_match),
        response=self.messages.StorageObjectsDeleteResponse())

    request_config = gcs_api.GcsRequestConfig(
        precondition_generation_match=precondition_generation_match)
    self.gcs_client.delete_object(
        TEST_BUCKET, TEST_OBJECT, request_config=request_config)

  def test_delete_object_precondition_metageneration_match(self):
    precondition_metageneration_match = 1
    self.apitools_client.objects.Delete.Expect(
        self.messages.StorageObjectsDeleteRequest(
            bucket=TEST_BUCKET,
            object=TEST_OBJECT,
            ifMetagenerationMatch=precondition_metageneration_match),
        response=self.messages.StorageObjectsDeleteResponse())

    request_config = gcs_api.GcsRequestConfig(
        precondition_metageneration_match=precondition_metageneration_match)
    self.gcs_client.delete_object(
        TEST_BUCKET, TEST_OBJECT, request_config=request_config)


class GetObjectMetadataTest(cloud_storage_util.WithGCSCalls,
                            parameterized.TestCase, sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageObjectsGetRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_get_object_metadata(self):
    metadata_object = self.messages.Object(name=TEST_OBJECT,
                                           bucket=TEST_BUCKET)
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        projection=self.default_projection)
    self.apitools_client.objects.Get.Expect(request,
                                            response=metadata_object)

    object_reference = self.gcs_client.get_object_metadata(
        TEST_BUCKET, TEST_OBJECT)
    expected_object_reference = gcs_api._object_resource_from_metadata(
        metadata_object)
    self.assertEqual(object_reference.metadata,
                     expected_object_reference.metadata)
    self.assertEqual(object_reference.storage_url,
                     expected_object_reference.storage_url)

  def test_get_object_metadata_api_error(self):
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        projection=self.default_projection)
    self.apitools_client.objects.Get.Expect(
        request, exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.get_object_metadata(TEST_BUCKET, TEST_OBJECT)

  def test_get_object_metadata_not_found_error(self):
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        projection=self.default_projection)
    self.apitools_client.objects.Get.Expect(
        request,
        exception=apitools_exceptions.HttpNotFoundError(None, None, None))

    with self.assertRaises(cloud_errors.NotFoundError):
      self.gcs_client.get_object_metadata(TEST_BUCKET, TEST_OBJECT)

  def test_get_object_metadata_generation(self):
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        generation=1,
        projection=self.default_projection)
    self.apitools_client.objects.Get.Expect(request,
                                            response=self.messages.Object())

    self.gcs_client.get_object_metadata(
        TEST_BUCKET, TEST_OBJECT, generation='1')

  def test_get_object_metadata_invalid_fields_scope(self):
    with self.assertRaises(ValueError):
      self.gcs_client.get_object_metadata(
          TEST_BUCKET, TEST_OBJECT, fields_scope='football field')

  @parameterized.parameters(
      (cloud_api.FieldsScope.SHORT, 'noAcl'),
      (cloud_api.FieldsScope.NO_ACL, 'noAcl'),
      (cloud_api.FieldsScope.FULL, 'full'))
  def test_get_object_metadata_valid_fields_scope(self, fields_scope,
                                                  projection):
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        projection=getattr(self.messages.StorageObjectsGetRequest
                           .ProjectionValueValuesEnum, projection))

    with mock.patch.object(self.apitools_client.objects, 'Get') as mock_get:
      self.gcs_client.get_object_metadata(
          TEST_BUCKET, TEST_OBJECT, fields_scope=fields_scope)
      mock_get.assert_called_once_with(request)


@test_case.Filters.DoNotRunOnPy2('Storage does not support Python 2.')
class PatchObjectMetadataTest(cloud_storage_util.WithGCSCalls,
                              parameterized.TestCase, sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageObjectsPatchRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_patch_object_metadata(self):
    patched_object = self.messages.Object()
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(request, response=patched_object)

    expected_resource = gcs_api._object_resource_from_metadata(patched_object)
    observed_resource = self.gcs_client.patch_object_metadata(
        TEST_BUCKET, TEST_OBJECT, expected_resource)
    self.assertEqual(observed_resource, expected_resource)

  def test_patch_object_metadata_populates_missing_metadata(self):
    return_metadata = self.messages.Object(name='o', bucket='b')
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=return_metadata,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(request, response=return_metadata)

    expected_resource = gcs_api._object_resource_from_metadata(return_metadata)
    patch_resource = test_resources.from_url_string('gs://b/o')
    observed_resource = self.gcs_client.patch_object_metadata(
        TEST_BUCKET, TEST_OBJECT, patch_resource)
    self.assertEqual(observed_resource, expected_resource)

  def test_patch_object_metadata_api_error(self):
    patched_object = self.messages.Object()
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(
        request, exception=apitools_exceptions.HttpError(None, None, None))
    object_resource = gcs_api._object_resource_from_metadata(patched_object)

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.patch_object_metadata(TEST_BUCKET, TEST_OBJECT,
                                            object_resource)

  def test_patch_object_metadata_generation(self):
    patched_object = self.messages.Object()
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        generation=1,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(request, response=patched_object)
    object_resource = gcs_api._object_resource_from_metadata(patched_object)

    self.gcs_client.patch_object_metadata(
        TEST_BUCKET, TEST_OBJECT, object_resource, generation='1')

  def test_patch_object_metadata_precondition_generation_match(self):
    patched_object = self.messages.Object()
    precondition_generation_match = 1
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        ifGenerationMatch=precondition_generation_match,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(request, response=patched_object)
    object_resource = gcs_api._object_resource_from_metadata(patched_object)

    self.gcs_client.patch_object_metadata(
        TEST_BUCKET,
        TEST_OBJECT,
        object_resource,
        request_config=gcs_api.GcsRequestConfig(
            precondition_generation_match=precondition_generation_match))

  def test_patch_object_metadata_precondition_metageneration_match(self):
    patched_object = self.messages.Object()
    precondition_metageneration_match = 1
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        ifMetagenerationMatch=precondition_metageneration_match,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(request, response=patched_object)
    object_resource = gcs_api._object_resource_from_metadata(patched_object)

    self.gcs_client.patch_object_metadata(
        TEST_BUCKET,
        TEST_OBJECT,
        object_resource,
        request_config=gcs_api.GcsRequestConfig(
            precondition_metageneration_match=precondition_metageneration_match)
    )

  def test_patch_object_metadata_predefined_acl_string(self):
    patched_object = self.messages.Object()
    predefined_acl_string = 'authenticatedRead'
    predefined_acl = getattr(
        self.messages.StorageObjectsPatchRequest.PredefinedAclValueValuesEnum,
        predefined_acl_string)

    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        predefinedAcl=predefined_acl,
        projection=self.default_projection)
    self.apitools_client.objects.Patch.Expect(request,
                                              response=self.messages.Object())

    request_config = gcs_api.GcsRequestConfig(
        predefined_acl_string=predefined_acl_string)
    object_resource = gcs_api._object_resource_from_metadata(patched_object)
    self.gcs_client.patch_object_metadata(
        TEST_BUCKET,
        TEST_OBJECT,
        object_resource,
        request_config=request_config)

  def test_patch_object_metadata_invalid_fields_scope(self):
    patched_object = self.messages.Object()
    object_resource = gcs_api._object_resource_from_metadata(patched_object)
    with self.assertRaises(ValueError):
      self.gcs_client.patch_object_metadata(
          TEST_BUCKET,
          TEST_OBJECT,
          object_resource,
          fields_scope='football field')

  @parameterized.parameters(
      (cloud_api.FieldsScope.SHORT, 'noAcl'),
      (cloud_api.FieldsScope.NO_ACL, 'noAcl'),
      (cloud_api.FieldsScope.FULL, 'full'))
  def test_patch_object_metadata_valid_fields_scope(self, fields_scope,
                                                    projection):
    patched_object = self.messages.Object()
    object_resource = gcs_api._object_resource_from_metadata(patched_object)
    request = self.messages.StorageObjectsPatchRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        objectResource=patched_object,
        projection=getattr(self.messages.StorageObjectsPatchRequest
                           .ProjectionValueValuesEnum, projection))

    with mock.patch.object(self.apitools_client.objects, 'Patch') as mock_patch:
      self.gcs_client.patch_object_metadata(
          TEST_BUCKET, TEST_OBJECT, object_resource, fields_scope=fields_scope)
      mock_patch.assert_called_once_with(request)


class CopyObjectTest(cloud_storage_util.WithGCSCalls, sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.default_projection = (self.messages.StorageObjectsPatchRequest
                               .ProjectionValueValuesEnum.noAcl)
    self.gcs_client = gcs_api.GcsApi()

  def test_copies_objects(self):
    source_resource = resource_reference.UnknownResource(
        storage_url.storage_url_from_string('gs://b/o'))
    destination_metadata = self.messages.Object(name='o2', bucket='b')
    destination_resource = resource_reference.UnknownResource(
        storage_url.storage_url_from_string('gs://b/o2'))

    request = self.messages.StorageObjectsCopyRequest(
        sourceBucket=source_resource.storage_url.bucket_name,
        sourceObject=source_resource.storage_url.object_name,
        destinationBucket=destination_resource.storage_url.bucket_name,
        destinationObject=destination_resource.storage_url.object_name)
    self.apitools_client.objects.Copy.Expect(request,
                                             response=destination_metadata)

    observed_resource = self.gcs_client.copy_object(source_resource,
                                                    destination_resource)
    expected_resource = gcs_api._object_resource_from_metadata(
        destination_metadata)
    self.assertEqual(observed_resource, expected_resource)

  def test_copy_handles_api_error(self):
    source_resource = resource_reference.UnknownResource(
        storage_url.storage_url_from_string('gs://b/o'))
    destination_resource = resource_reference.UnknownResource(
        storage_url.storage_url_from_string('gs://b/o2'))

    request = self.messages.StorageObjectsCopyRequest(
        sourceBucket=source_resource.storage_url.bucket_name,
        sourceObject=source_resource.storage_url.object_name,
        destinationBucket=destination_resource.storage_url.bucket_name,
        destinationObject=destination_resource.storage_url.object_name)
    self.apitools_client.objects.Copy.Expect(
        request, exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.copy_object(source_resource, destination_resource)

  def test_copy_handles_generation(self):
    source_resource = resource_reference.UnknownResource(
        storage_url.storage_url_from_string('gs://b/o'))
    destination_metadata = self.messages.Object(name='o2', bucket='b')
    destination_resource = resource_reference.UnknownResource(
        storage_url.storage_url_from_string('gs://b/o2'))

    request = self.messages.StorageObjectsCopyRequest(
        sourceBucket=source_resource.storage_url.bucket_name,
        sourceObject=source_resource.storage_url.object_name,
        destinationBucket=destination_resource.storage_url.bucket_name,
        destinationObject=destination_resource.storage_url.object_name,
        ifSourceGenerationMatch=1)
    self.apitools_client.objects.Copy.Expect(request,
                                             response=destination_metadata)

    request_config = gcs_api.GcsRequestConfig(precondition_generation_match=1)
    observed_resource = self.gcs_client.copy_object(
        source_resource, destination_resource, request_config=request_config)
    expected_resource = gcs_api._object_resource_from_metadata(
        destination_metadata)
    self.assertEqual(observed_resource, expected_resource)

  # TODO(b/161900052): Test resumable copies.
  # TODO(b/161898251): Test encryption and decryption.


class DownloadObjectTest(cloud_storage_util.WithGCSCalls,
                         sdk_test_base.WithFakeAuth):

  def SetUp(self):
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.gcs_client = gcs_api.GcsApi()
    self.download_stream = mock.mock_open()

  @mock.patch.object(apitools_transfer.Download, 'FromStream')
  def test_object_download(self, mock_from_stream):
    mock_from_stream.return_value = mock.Mock(
        autospec=apitools_transfer.Download)
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
    )
    self.apitools_client.objects.Get.Expect(
        request, response=self.messages.Object())

    self.gcs_client.download_object(TEST_BUCKET, TEST_OBJECT,
                                    self.download_stream)
    mock_from_stream.assert_called_once_with(
        self.download_stream,
        auto_transfer=False,
        total_size=None,
        num_retries=gcs_api.DEFAULT_NUM_RETRIES)

  @mock.patch.object(apitools_transfer.Download, 'FromStream')
  def test_object_download_api_error(self, mock_from_stream):
    mock_from_stream.return_value = mock.Mock(
        autospec=apitools_transfer.Download)
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
    )
    self.apitools_client.objects.Get.Expect(
        request, exception=apitools_exceptions.HttpError(None, None, None))

    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.download_object(TEST_BUCKET, TEST_OBJECT,
                                      self.download_stream)

  @mock.patch.object(apitools_transfer.Download, 'FromStream')
  def test_object_download_compressed_encoding(self, mock_from_stream):
    mock_download = mock.Mock(autospec=apitools_transfer.Download)
    mock_download.StreamMedia = mock.Mock()
    mock_from_stream.return_value = mock_download
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
    )
    self.apitools_client.objects.Get.Expect(
        request, response=self.messages.Object())

    self.gcs_client.download_object(
        TEST_BUCKET,
        TEST_OBJECT,
        self.download_stream,
        compressed_encoding=True)

    mock_download.StreamMedia.assert_called_once_with(
        additional_headers={'accept-encoding': 'gzip'},
        callback=gcs_api._no_op_callback,
        finish_callback=gcs_api._no_op_callback,
        use_chunks=False)

  @mock.patch.object(apitools_transfer.Download, 'FromStream')
  def test_object_download_generation(self, mock_from_stream):
    mock_from_stream.return_value = mock.Mock(
        autospec=apitools_transfer.Download)
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT,
        generation=1)
    self.apitools_client.objects.Get.Expect(
        request, response=self.messages.Object())

    self.gcs_client.download_object(
        TEST_BUCKET, TEST_OBJECT, self.download_stream, generation='1')

  @mock.patch.object(apitools_transfer.Download, 'FromStream')
  def test_object_download_object_size(self, mock_from_stream):
    mock_from_stream.return_value = mock.Mock(
        autospec=apitools_transfer.Download)
    object_size = 1
    request = self.messages.StorageObjectsGetRequest(
        bucket=TEST_BUCKET,
        object=TEST_OBJECT)
    self.apitools_client.objects.Get.Expect(
        request, response=self.messages.Object())

    self.gcs_client.download_object(
        TEST_BUCKET, TEST_OBJECT, self.download_stream, object_size=object_size)

    mock_from_stream.assert_called_once_with(
        self.download_stream,
        auto_transfer=False,
        total_size=object_size,
        num_retries=gcs_api.DEFAULT_NUM_RETRIES)

  # TODO(b/161437904): Tests for the decryption parameter.
  # TODO(b/161437901): Tests for resumable downloads.


class UploadObjectTest(cloud_storage_util.WithGCSCalls, parameterized.TestCase,
                       sdk_test_base.SdkBase):

  def SetUp(self):
    properties.VALUES.core.account.Set(TEST_ACCOUNT)
    properties.VALUES.core.project.Set(TEST_PROJECT)
    self.messages = core_apis.GetMessagesModule('storage', 'v1')
    self.gcs_client = gcs_api.GcsApi()

  def test_uploads_object_with_object_resource(self):
    upload_metadata = self.messages.Object(name='o', bucket='b')
    request = self.messages.StorageObjectsInsertRequest(
        bucket=upload_metadata.bucket,
        object=upload_metadata)
    self.apitools_client.objects.Insert.Expect(request,
                                               response=upload_metadata)

    upload_stream = mock.mock_open()
    upload_resource = resource_reference.FileObjectResource(
        storage_url.storage_url_from_string('gs://b/o'))
    expected_resource = gcs_api._object_resource_from_metadata(upload_metadata)
    with mock.patch.object(apitools_transfer, 'Upload') as mock_upload:
      observed_resource = self.gcs_client.upload_object(upload_stream,
                                                        upload_resource)
      self.assertEqual(observed_resource, expected_resource)

      mock_upload.assert_called_once_with(
          upload_stream,
          gcs_api.DEFAULT_CONTENT_TYPE,
          total_size=None,
          auto_transfer=True,
          num_retries=gcs_api.DEFAULT_NUM_RETRIES,
          gzip_encoded=False)

  def test_object_upload_handles_api_error(self):
    upload_metadata = self.messages.Object(name='o', bucket='b')
    request = self.messages.StorageObjectsInsertRequest(
        bucket=upload_metadata.bucket,
        object=upload_metadata)
    self.apitools_client.objects.Insert.Expect(
        request, exception=apitools_exceptions.HttpError(None, None, None))

    upload_resource = resource_reference.FileObjectResource(
        storage_url.storage_url_from_string('gs://b/o'))
    with self.assertRaises(cloud_errors.GcsApiError):
      self.gcs_client.upload_object(mock.mock_open(), upload_resource)

  def test_object_upload_predefined_acl_string(self):
    upload_metadata = self.messages.Object(name='o', bucket='b')
    predefined_acl_string = 'authenticatedRead'
    predefined_acl = getattr(
        self.messages.StorageObjectsInsertRequest.PredefinedAclValueValuesEnum,
        predefined_acl_string)

    request = self.messages.StorageObjectsInsertRequest(
        bucket=upload_metadata.bucket,
        object=upload_metadata,
        predefinedAcl=predefined_acl)
    self.apitools_client.objects.Insert.Expect(request,
                                               response=upload_metadata)

    request_config = gcs_api.GcsRequestConfig(
        predefined_acl_string=predefined_acl_string)
    upload_resource = resource_reference.FileObjectResource(
        storage_url.storage_url_from_string('gs://b/o'))
    self.gcs_client.upload_object(
        mock.mock_open(), upload_resource, request_config=request_config)

  def test_object_upload_gzip_encoded(self):
    upload_metadata = self.messages.Object(name='o', bucket='b')
    request = self.messages.StorageObjectsInsertRequest(
        bucket=upload_metadata.bucket,
        object=upload_metadata)
    self.apitools_client.objects.Insert.Expect(request,
                                               response=upload_metadata)

    upload_stream = mock.mock_open()
    upload_resource = resource_reference.FileObjectResource(
        storage_url.storage_url_from_string('gs://b/o'))
    with mock.patch.object(apitools_transfer, 'Upload') as mock_upload:
      request_config = gcs_api.GcsRequestConfig(gzip_encoded=True)
      self.gcs_client.upload_object(
          upload_stream, upload_resource, request_config=request_config)

      mock_upload.assert_called_once_with(
          upload_stream,
          gcs_api.DEFAULT_CONTENT_TYPE,
          total_size=None,
          auto_transfer=True,
          num_retries=gcs_api.DEFAULT_NUM_RETRIES,
          gzip_encoded=True)

  # TODO(b/160998052): Tests for the encryption_wrapper parameter.
  # TODO(b/160998556): Tests for resumable uploads.


if __name__ == '__main__':
  test_case.main()
