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
"""This is a command for testing."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base


class RequiredOtherFlags(calliope_base.Command):
  """A command with required+other flags."""

  @staticmethod
  def Args(parser):
    parser.add_argument('--required', required=True,
                        help='This flag is required.')
    parser.add_argument('--other',
                        help='This flag is other.')

  def Run(self, args):
    pass
