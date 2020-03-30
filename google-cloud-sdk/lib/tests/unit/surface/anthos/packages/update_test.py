# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""anthos sync tests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os

from googlecloudsdk.command_lib.util.anthos import binary_operations
from tests.lib import test_case
from tests.lib.surface.anthos import test_base as anthos_test_base


class UpdateTest(anthos_test_base.PackageUnitTestBase):

  def SetUp(self):
    self.test_package = self.Touch(
        os.path.join(self.home_path, 'my-package-dir'),
        name='temp',
        makedirs=True)

  def testUpdate(self):
    working_dir = self.CreateTempDir('my-package-dir')
    self.Run('anthos packages update {package} '
             '--repo-uri https://github.com/my-other-account/foo.git '
             '--strategy force-delete-replace'.format(package=working_dir))
    self.AssertValidBinaryCall(
        env={'COBRA_SILENCE_USAGE': 'true', 'GCLOUD_AUTH_PLUGIN': 'true'},
        command_args=[
            anthos_test_base._MOCK_ANTHOS_BINARY,
            'update',
            '.',
            '--repo',
            'https://github.com/my-other-account/foo.git',
            '--strategy',
            'force-delete-replace'])

  def testUpdateWithEmptyRef(self):
    working_dir = self.CreateTempDir('my-package-dir')
    self.Run('anthos packages update {package}@ '
             '--repo-uri https://github.com/my-other-account/foo.git '
             '--strategy force-delete-replace'.format(package=working_dir))
    self.AssertValidBinaryCall(
        env={'COBRA_SILENCE_USAGE': 'true', 'GCLOUD_AUTH_PLUGIN': 'true'},
        command_args=[
            anthos_test_base._MOCK_ANTHOS_BINARY,
            'update',
            '.',
            '--repo',
            'https://github.com/my-other-account/foo.git',
            '--strategy',
            'force-delete-replace'])

  def testUpdateWithRef(self):
    working_dir = self.CreateTempDir('my-package-dir')
    self.Run('anthos packages update {package}@v1.3 '
             '--repo-uri https://github.com/my-other-account/foo.git '
             '--strategy force-delete-replace'.format(package=working_dir))
    self.AssertValidBinaryCall(
        env={'COBRA_SILENCE_USAGE': 'true', 'GCLOUD_AUTH_PLUGIN': 'true'},
        command_args=[
            anthos_test_base._MOCK_ANTHOS_BINARY,
            'update',
            '.@v1.3',
            '--repo',
            'https://github.com/my-other-account/foo.git',
            '--strategy',
            'force-delete-replace'])

  def testUpdateWithMissingPackage(self):
    with self.assertRaises(binary_operations.InvalidWorkingDirectoryError):
      self.Run('anthos packages update fake-package@v1.3 '
               '--repo-uri https://github.com/my-other-account/foo.git '
               '--strategy force-delete-replace')


if __name__ == '__main__':
  test_case.main()
