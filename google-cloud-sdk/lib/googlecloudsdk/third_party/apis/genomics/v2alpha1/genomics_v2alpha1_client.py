"""Generated client library for genomics version v2alpha1."""
# NOTE: This file is autogenerated and should not be edited by hand.

from __future__ import absolute_import

from apitools.base.py import base_api
from googlecloudsdk.third_party.apis.genomics.v2alpha1 import genomics_v2alpha1_messages as messages


class GenomicsV2alpha1(base_api.BaseApiClient):
  """Generated client library for service genomics version v2alpha1."""

  MESSAGES_MODULE = messages
  BASE_URL = 'https://genomics.googleapis.com/'
  MTLS_BASE_URL = 'https://genomics.mtls.googleapis.com/'

  _PACKAGE = 'genomics'
  _SCOPES = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/genomics']
  _VERSION = 'v2alpha1'
  _CLIENT_ID = '1042881264118.apps.googleusercontent.com'
  _CLIENT_SECRET = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _USER_AGENT = 'google-cloud-sdk'
  _CLIENT_CLASS_NAME = 'GenomicsV2alpha1'
  _URL_VERSION = 'v2alpha1'
  _API_KEY = None

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None, response_encoding=None):
    """Create a new genomics handle."""
    url = url or self.BASE_URL
    super(GenomicsV2alpha1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers,
        response_encoding=response_encoding)
    self.pipelines = self.PipelinesService(self)
    self.projects_operations = self.ProjectsOperationsService(self)
    self.projects_workers = self.ProjectsWorkersService(self)
    self.projects = self.ProjectsService(self)
    self.workers = self.WorkersService(self)

  class PipelinesService(base_api.BaseApiService):
    """Service class for the pipelines resource."""

    _NAME = 'pipelines'

    def __init__(self, client):
      super(GenomicsV2alpha1.PipelinesService, self).__init__(client)
      self._upload_configs = {
          }

    def Run(self, request, global_params=None):
      r"""Runs a pipeline. The returned Operation's metadata field will contain a google.genomics.v2alpha1.Metadata object describing the status of the pipeline execution. The [response] field will contain a google.genomics.v2alpha1.RunPipelineResponse object if the pipeline completes successfully. **Note:** Before you can use this method, the Genomics Service Agent must have access to your project. This is done automatically when the Cloud Genomics API is first enabled, but if you delete this permission, or if you enabled the Cloud Genomics API before the v2alpha1 API launch, you must disable and re-enable the API to grant the Genomics Service Agent the required permissions. Authorization requires the following [Google IAM](https://cloud.google.com/iam/) permission: * `genomics.operations.create` [1]: /genomics/gsa.

      Args:
        request: (RunPipelineRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Run')
      return self._RunMethod(
          config, request, global_params=global_params)

    Run.method_config = lambda: base_api.ApiMethodInfo(
        http_method='POST',
        method_id='genomics.pipelines.run',
        ordered_params=[],
        path_params=[],
        query_params=[],
        relative_path='v2alpha1/pipelines:run',
        request_field='<request>',
        request_type_name='RunPipelineRequest',
        response_type_name='Operation',
        supports_download=False,
    )

  class ProjectsOperationsService(base_api.BaseApiService):
    """Service class for the projects_operations resource."""

    _NAME = 'projects_operations'

    def __init__(self, client):
      super(GenomicsV2alpha1.ProjectsOperationsService, self).__init__(client)
      self._upload_configs = {
          }

    def Cancel(self, request, global_params=None):
      r"""Starts asynchronous cancellation on a long-running operation. The server makes a best effort to cancel the operation, but success is not guaranteed. Clients may use Operations.GetOperation or Operations.ListOperations to check whether the cancellation succeeded or the operation completed despite cancellation. Authorization requires the following [Google IAM](https://cloud.google.com/iam) permission: * `genomics.operations.cancel`.

      Args:
        request: (GenomicsProjectsOperationsCancelRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Cancel')
      return self._RunMethod(
          config, request, global_params=global_params)

    Cancel.method_config = lambda: base_api.ApiMethodInfo(
        flat_path='v2alpha1/projects/{projectsId}/operations/{operationsId}:cancel',
        http_method='POST',
        method_id='genomics.projects.operations.cancel',
        ordered_params=['name'],
        path_params=['name'],
        query_params=[],
        relative_path='v2alpha1/{+name}:cancel',
        request_field='cancelOperationRequest',
        request_type_name='GenomicsProjectsOperationsCancelRequest',
        response_type_name='Empty',
        supports_download=False,
    )

    def Get(self, request, global_params=None):
      r"""Gets the latest state of a long-running operation. Clients can use this method to poll the operation result at intervals as recommended by the API service. Authorization requires the following [Google IAM](https://cloud.google.com/iam) permission: * `genomics.operations.get`.

      Args:
        request: (GenomicsProjectsOperationsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    Get.method_config = lambda: base_api.ApiMethodInfo(
        flat_path='v2alpha1/projects/{projectsId}/operations/{operationsId}',
        http_method='GET',
        method_id='genomics.projects.operations.get',
        ordered_params=['name'],
        path_params=['name'],
        query_params=[],
        relative_path='v2alpha1/{+name}',
        request_field='',
        request_type_name='GenomicsProjectsOperationsGetRequest',
        response_type_name='Operation',
        supports_download=False,
    )

    def List(self, request, global_params=None):
      r"""Lists operations that match the specified filter in the request. Authorization requires the following [Google IAM](https://cloud.google.com/iam) permission: * `genomics.operations.list`.

      Args:
        request: (GenomicsProjectsOperationsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListOperationsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path='v2alpha1/projects/{projectsId}/operations',
        http_method='GET',
        method_id='genomics.projects.operations.list',
        ordered_params=['name'],
        path_params=['name'],
        query_params=['filter', 'pageSize', 'pageToken'],
        relative_path='v2alpha1/{+name}',
        request_field='',
        request_type_name='GenomicsProjectsOperationsListRequest',
        response_type_name='ListOperationsResponse',
        supports_download=False,
    )

  class ProjectsWorkersService(base_api.BaseApiService):
    """Service class for the projects_workers resource."""

    _NAME = 'projects_workers'

    def __init__(self, client):
      super(GenomicsV2alpha1.ProjectsWorkersService, self).__init__(client)
      self._upload_configs = {
          }

    def CheckIn(self, request, global_params=None):
      r"""The worker uses this method to retrieve the assigned operation and provide periodic status updates.

      Args:
        request: (GenomicsProjectsWorkersCheckInRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (CheckInResponse) The response message.
      """
      config = self.GetMethodConfig('CheckIn')
      return self._RunMethod(
          config, request, global_params=global_params)

    CheckIn.method_config = lambda: base_api.ApiMethodInfo(
        flat_path='v2alpha1/projects/{projectsId}/workers/{workersId}:checkIn',
        http_method='POST',
        method_id='genomics.projects.workers.checkIn',
        ordered_params=['id'],
        path_params=['id'],
        query_params=[],
        relative_path='v2alpha1/{+id}:checkIn',
        request_field='checkInRequest',
        request_type_name='GenomicsProjectsWorkersCheckInRequest',
        response_type_name='CheckInResponse',
        supports_download=False,
    )

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = 'projects'

    def __init__(self, client):
      super(GenomicsV2alpha1.ProjectsService, self).__init__(client)
      self._upload_configs = {
          }

  class WorkersService(base_api.BaseApiService):
    """Service class for the workers resource."""

    _NAME = 'workers'

    def __init__(self, client):
      super(GenomicsV2alpha1.WorkersService, self).__init__(client)
      self._upload_configs = {
          }

    def CheckIn(self, request, global_params=None):
      r"""The worker uses this method to retrieve the assigned operation and provide periodic status updates.

      Args:
        request: (GenomicsWorkersCheckInRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (CheckInResponse) The response message.
      """
      config = self.GetMethodConfig('CheckIn')
      return self._RunMethod(
          config, request, global_params=global_params)

    CheckIn.method_config = lambda: base_api.ApiMethodInfo(
        http_method='POST',
        method_id='genomics.workers.checkIn',
        ordered_params=['id'],
        path_params=['id'],
        query_params=[],
        relative_path='v2alpha1/workers/{id}:checkIn',
        request_field='checkInRequest',
        request_type_name='GenomicsWorkersCheckInRequest',
        response_type_name='CheckInResponse',
        supports_download=False,
    )
