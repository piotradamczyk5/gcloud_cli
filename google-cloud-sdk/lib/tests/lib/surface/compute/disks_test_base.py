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
"""Test calliope_base for compute disks unit tests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.core import resources
from tests.lib.surface.compute import test_base


class TestBase(test_base.BaseTest):
  """Base class for disks tests."""

  def SetUpTrack(self, track):
    if track == calliope_base.ReleaseTrack.ALPHA:
      self.api_version = 'alpha'
    elif track == calliope_base.ReleaseTrack.BETA:
      self.api_version = 'beta'
    else:
      self.api_version = 'v1'
    self.SelectApi(self.api_version)
    self.track = track
    self.disk_name = 'my-disk'
    self.zone = 'central2-a'
    self.region = 'central2'
    self.reg = resources.REGISTRY.Clone()
    self.reg.RegisterApiByName('compute', self.api_version)

  def SetUp(self):
    self.SetUpTrack(self.track)
