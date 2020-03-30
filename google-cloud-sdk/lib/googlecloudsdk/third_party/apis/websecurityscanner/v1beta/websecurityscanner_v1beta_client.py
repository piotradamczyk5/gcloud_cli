"""Generated client library for websecurityscanner version v1beta."""
# NOTE: This file is autogenerated and should not be edited by hand.
from apitools.base.py import base_api
from googlecloudsdk.third_party.apis.websecurityscanner.v1beta import websecurityscanner_v1beta_messages as messages


class WebsecurityscannerV1beta(base_api.BaseApiClient):
  """Generated client library for service websecurityscanner version v1beta."""

  MESSAGES_MODULE = messages
  BASE_URL = u'https://websecurityscanner.googleapis.com/'
  MTLS_BASE_URL = u'https://websecurityscanner.mtls.googleapis.com/'

  _PACKAGE = u'websecurityscanner'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform']
  _VERSION = u'v1beta'
  _CLIENT_ID = '1042881264118.apps.googleusercontent.com'
  _CLIENT_SECRET = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _USER_AGENT = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _CLIENT_CLASS_NAME = u'WebsecurityscannerV1beta'
  _URL_VERSION = u'v1beta'
  _API_KEY = None

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None, response_encoding=None):
    """Create a new websecurityscanner handle."""
    url = url or self.BASE_URL
    super(WebsecurityscannerV1beta, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers,
        response_encoding=response_encoding)
    self.projects_scanConfigs_scanRuns_crawledUrls = self.ProjectsScanConfigsScanRunsCrawledUrlsService(self)
    self.projects_scanConfigs_scanRuns_findingTypeStats = self.ProjectsScanConfigsScanRunsFindingTypeStatsService(self)
    self.projects_scanConfigs_scanRuns_findings = self.ProjectsScanConfigsScanRunsFindingsService(self)
    self.projects_scanConfigs_scanRuns = self.ProjectsScanConfigsScanRunsService(self)
    self.projects_scanConfigs = self.ProjectsScanConfigsService(self)
    self.projects = self.ProjectsService(self)

  class ProjectsScanConfigsScanRunsCrawledUrlsService(base_api.BaseApiService):
    """Service class for the projects_scanConfigs_scanRuns_crawledUrls resource."""

    _NAME = u'projects_scanConfigs_scanRuns_crawledUrls'

    def __init__(self, client):
      super(WebsecurityscannerV1beta.ProjectsScanConfigsScanRunsCrawledUrlsService, self).__init__(client)
      self._upload_configs = {
          }

    def List(self, request, global_params=None):
      r"""List CrawledUrls under a given ScanRun.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsCrawledUrlsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListCrawledUrlsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns/{scanRunsId}/crawledUrls',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.crawledUrls.list',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[u'pageSize', u'pageToken'],
        relative_path=u'v1beta/{+parent}/crawledUrls',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsCrawledUrlsListRequest',
        response_type_name=u'ListCrawledUrlsResponse',
        supports_download=False,
    )

  class ProjectsScanConfigsScanRunsFindingTypeStatsService(base_api.BaseApiService):
    """Service class for the projects_scanConfigs_scanRuns_findingTypeStats resource."""

    _NAME = u'projects_scanConfigs_scanRuns_findingTypeStats'

    def __init__(self, client):
      super(WebsecurityscannerV1beta.ProjectsScanConfigsScanRunsFindingTypeStatsService, self).__init__(client)
      self._upload_configs = {
          }

    def List(self, request, global_params=None):
      r"""List all FindingTypeStats under a given ScanRun.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsFindingTypeStatsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListFindingTypeStatsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns/{scanRunsId}/findingTypeStats',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.findingTypeStats.list',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[],
        relative_path=u'v1beta/{+parent}/findingTypeStats',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsFindingTypeStatsListRequest',
        response_type_name=u'ListFindingTypeStatsResponse',
        supports_download=False,
    )

  class ProjectsScanConfigsScanRunsFindingsService(base_api.BaseApiService):
    """Service class for the projects_scanConfigs_scanRuns_findings resource."""

    _NAME = u'projects_scanConfigs_scanRuns_findings'

    def __init__(self, client):
      super(WebsecurityscannerV1beta.ProjectsScanConfigsScanRunsFindingsService, self).__init__(client)
      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      r"""Gets a Finding.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsFindingsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Finding) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    Get.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns/{scanRunsId}/findings/{findingsId}',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.findings.get',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1beta/{+name}',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsFindingsGetRequest',
        response_type_name=u'Finding',
        supports_download=False,
    )

    def List(self, request, global_params=None):
      r"""List Findings under a given ScanRun.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsFindingsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListFindingsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns/{scanRunsId}/findings',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.findings.list',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[u'filter', u'pageSize', u'pageToken'],
        relative_path=u'v1beta/{+parent}/findings',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsFindingsListRequest',
        response_type_name=u'ListFindingsResponse',
        supports_download=False,
    )

  class ProjectsScanConfigsScanRunsService(base_api.BaseApiService):
    """Service class for the projects_scanConfigs_scanRuns resource."""

    _NAME = u'projects_scanConfigs_scanRuns'

    def __init__(self, client):
      super(WebsecurityscannerV1beta.ProjectsScanConfigsScanRunsService, self).__init__(client)
      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      r"""Gets a ScanRun.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ScanRun) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    Get.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns/{scanRunsId}',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.get',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1beta/{+name}',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsGetRequest',
        response_type_name=u'ScanRun',
        supports_download=False,
    )

    def List(self, request, global_params=None):
      r"""Lists ScanRuns under a given ScanConfig, in descending order of ScanRun.
stop time.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListScanRunsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.list',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[u'pageSize', u'pageToken'],
        relative_path=u'v1beta/{+parent}/scanRuns',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsListRequest',
        response_type_name=u'ListScanRunsResponse',
        supports_download=False,
    )

    def Stop(self, request, global_params=None):
      r"""Stops a ScanRun. The stopped ScanRun is returned.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsScanRunsStopRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ScanRun) The response message.
      """
      config = self.GetMethodConfig('Stop')
      return self._RunMethod(
          config, request, global_params=global_params)

    Stop.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}/scanRuns/{scanRunsId}:stop',
        http_method=u'POST',
        method_id=u'websecurityscanner.projects.scanConfigs.scanRuns.stop',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1beta/{+name}:stop',
        request_field=u'stopScanRunRequest',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsScanRunsStopRequest',
        response_type_name=u'ScanRun',
        supports_download=False,
    )

  class ProjectsScanConfigsService(base_api.BaseApiService):
    """Service class for the projects_scanConfigs resource."""

    _NAME = u'projects_scanConfigs'

    def __init__(self, client):
      super(WebsecurityscannerV1beta.ProjectsScanConfigsService, self).__init__(client)
      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      r"""Creates a new ScanConfig.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ScanConfig) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    Create.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs',
        http_method=u'POST',
        method_id=u'websecurityscanner.projects.scanConfigs.create',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[],
        relative_path=u'v1beta/{+parent}/scanConfigs',
        request_field=u'scanConfig',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsCreateRequest',
        response_type_name=u'ScanConfig',
        supports_download=False,
    )

    def Delete(self, request, global_params=None):
      r"""Deletes an existing ScanConfig and its child resources.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    Delete.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}',
        http_method=u'DELETE',
        method_id=u'websecurityscanner.projects.scanConfigs.delete',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1beta/{+name}',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsDeleteRequest',
        response_type_name=u'Empty',
        supports_download=False,
    )

    def Get(self, request, global_params=None):
      r"""Gets a ScanConfig.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ScanConfig) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    Get.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.get',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1beta/{+name}',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsGetRequest',
        response_type_name=u'ScanConfig',
        supports_download=False,
    )

    def List(self, request, global_params=None):
      r"""Lists ScanConfigs under a given project.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListScanConfigsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs',
        http_method=u'GET',
        method_id=u'websecurityscanner.projects.scanConfigs.list',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[u'pageSize', u'pageToken'],
        relative_path=u'v1beta/{+parent}/scanConfigs',
        request_field='',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsListRequest',
        response_type_name=u'ListScanConfigsResponse',
        supports_download=False,
    )

    def Patch(self, request, global_params=None):
      r"""Updates a ScanConfig. This method support partial update of a ScanConfig.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ScanConfig) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    Patch.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}',
        http_method=u'PATCH',
        method_id=u'websecurityscanner.projects.scanConfigs.patch',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[u'updateMask'],
        relative_path=u'v1beta/{+name}',
        request_field=u'scanConfig',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsPatchRequest',
        response_type_name=u'ScanConfig',
        supports_download=False,
    )

    def Start(self, request, global_params=None):
      r"""Start a ScanRun according to the given ScanConfig.

      Args:
        request: (WebsecurityscannerProjectsScanConfigsStartRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ScanRun) The response message.
      """
      config = self.GetMethodConfig('Start')
      return self._RunMethod(
          config, request, global_params=global_params)

    Start.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1beta/projects/{projectsId}/scanConfigs/{scanConfigsId}:start',
        http_method=u'POST',
        method_id=u'websecurityscanner.projects.scanConfigs.start',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1beta/{+name}:start',
        request_field=u'startScanRunRequest',
        request_type_name=u'WebsecurityscannerProjectsScanConfigsStartRequest',
        response_type_name=u'ScanRun',
        supports_download=False,
    )

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(WebsecurityscannerV1beta.ProjectsService, self).__init__(client)
      self._upload_configs = {
          }
