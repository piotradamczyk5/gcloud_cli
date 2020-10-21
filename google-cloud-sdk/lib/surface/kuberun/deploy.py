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
"""Command to list available Kuberun resources."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.kuberun import kuberun_command
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'EXAMPLES':
        """
        To deploy KubeRun application, run:

            $ {command}
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Deploy(kuberun_command.KubeRunStreamingCommand, base.CreateCommand):
  """Deploy KubeRun application."""

  detailed_help = _DETAILED_HELP
  flags = []

  @classmethod
  def Args(cls, parser):
    super(Deploy, cls).Args(parser)
    base.URI_FLAG.RemoveFromParser(parser)

  def Command(self):
    return ['deploy']

  def FormatOutput(self, out, args):
    if not out:
      return out
    return out + '\n'

  def Display(self, args, output):
    log.out.write(output)
