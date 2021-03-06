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

"""Tests for the instances tail-serial-port-output subcommand."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.core import exceptions as core_exceptions
from tests.lib import test_case
from tests.lib.surface.compute import test_base


CONTENTS = textwrap.dedent("""\
    Changing serial settings was 0/0 now 3/0
    Start bios (version 1.7.2-20131007_152402-google)
    No Xen hypervisor found.
    Unable to unlock ram - bridge not found
    Ram Size=0xc0000000 (0x0000000030000000 high)
    Relocating low data from 0x000e10a0 to 0x000ef780 (size 2161)
    Relocating init from 0x000e1911 to 0xbffd07a0 (size 63291)
    CPU Mhz=2600
    === PCI bus & bridge init ===
    PCI: pci_bios_init_bus_rec bus = 0x0
    === PCI device probing ===
    Found 4 PCI devices (max PCI bus is 00)
    === PCI new allocation pass #1 ===
    PCI: check devices
    === PCI new allocation pass #2 ===
    PCI: map device bdf=00:03.0  bar 0, addr 0000c000, size 00000040 [io]
    PCI: map device bdf=00:04.0  bar 0, addr 0000c040, size 00000020 [io]
    PCI: init bdf=00:01.0 id=8086:7110
    PIIX3/PIIX4 init: elcr=00 0c
    PCI: init bdf=00:01.3 id=8086:7113
    Using pmtimer, ioport 0xb008, freq 3579 kHz
    PCI: init bdf=00:03.0 id=1af4:1004
    PCI: init bdf=00:04.0 id=1af4:1000
    Found 1 cpu(s) max supported 1 cpu(s)
    MP table addr=0x000fdaf0 MPC table addr=0x000fdb00 size=240
    SMBIOS ptr=0x000fdad0 table=0x000fd990 size=307
    Memory hotplug not enabled. [MHPE=0xffffffff]
    ACPI DSDT=0xbfffe1f0
    ACPI tables: RSDP=0x000fd960 RSDT=0xbfffe1c0
    Scan for VGA option rom
    WARNING - Timeout at i8042_flush:68!
    All threads complete.
    Found 0 lpt ports
    Found 0 serial ports
    found virtio-scsi at 0:3
    Searching bootorder for: /pci@i0cf8/*@3/*@0/*@0,0
    Searching bootorder for: /pci@i0cf8/*@3/*@0/*@1,0
    virtio-scsi vendor='Google' product='PersistentDisk' rev='1' type=0 removable=0
    virtio-scsi blksize=512 sectors=20971520
    """)


class InstancesGetSerialPortOutputTest(test_base.BaseTest,
                                       test_case.WithOutputCapture):

  def SetUp(self):
    self.make_requests.side_effect = iter([
        [self.messages.SerialPortOutput(contents=CONTENTS, next=len(CONTENTS))],
        [self.messages.SerialPortOutput(contents='', next=len(CONTENTS))],
    ])

  def testWithInstanceName(self):
    sleep_mock = self.StartPatch('time.sleep', autospec=True)
    sleep_mock.side_effect = calliope_exceptions.ToolException(
        'raise_after_second_request')
    with self.AssertRaisesToolExceptionMatches('raise_after_second_request'):
      self.Run("""
          compute instances tail-serial-port-output instance-1
          --zone central2-a
          """)

    self.CheckRequests(
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              zone='central2-a'))],
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              start=len(CONTENTS),
              zone='central2-a'))],
    )
    self.AssertOutputEquals(CONTENTS)

  def testUriSupport(self):
    sleep_mock = self.StartPatch('time.sleep', autospec=True)
    sleep_mock.side_effect = calliope_exceptions.ToolException(
        'raise_after_second_request')
    with self.AssertRaisesToolExceptionMatches('raise_after_second_request'):
      self.Run("""
          compute instances tail-serial-port-output
          https://compute.googleapis.com/compute/v1/projects/my-project/zones/central2-a/instances/instance-1
          """)

    self.CheckRequests(
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              zone='central2-a'))],
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              start=len(CONTENTS),
              zone='central2-a'))],
    )
    self.AssertOutputEquals(CONTENTS)

  def testZonePrompting(self):
    self.StartPatch('googlecloudsdk.core.console.console_io.CanPrompt',
                    return_value=True)
    self.make_requests.side_effect = iter([
        [
            self.messages.Instance(name='instance-1', zone='zone-1'),
        ],

        [self.messages.SerialPortOutput(contents=CONTENTS,
                                        next=len(CONTENTS))],
        [self.messages.SerialPortOutput(contents='', next=len(CONTENTS))],
    ])

    sleep_mock = self.StartPatch('time.sleep', autospec=True)
    sleep_mock.side_effect = calliope_exceptions.ToolException(
        'raise_after_second_request')
    with self.AssertRaisesToolExceptionMatches('raise_after_second_request'):
      self.Run("""
          compute instances tail-serial-port-output instance-1
          """)

    self.CheckRequests(
        self.FilteredInstanceAggregateListRequest('instance-1'),

        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              zone='zone-1'))],
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              start=len(CONTENTS),
              zone='zone-1'))],
    )
    self.AssertErrContains(
        'No zone specified. Using zone [zone-1] for instance: [instance-1].')
    self.AssertOutputEquals(CONTENTS)

  def testWithNonExistentInstance(self):
    def MakeRequests(*_, **kwargs):
      if False:  # pylint: disable=using-constant-test
        yield
      kwargs['errors'].append((404, 'Not Found'))

    self.make_requests.side_effect = MakeRequests

    with self.assertRaisesRegex(
        core_exceptions.Error,
        'Could not fetch serial port output: Not Found'):
      self.Run("""
          compute instances tail-serial-port-output instance-1
            --zone central2-a
          """)

    self.CheckRequests(
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              zone='central2-a'))],
    )
    self.assertFalse(self.GetOutput())

  def testWithPortArgument(self):
    sleep_mock = self.StartPatch('time.sleep', autospec=True)
    sleep_mock.side_effect = calliope_exceptions.ToolException(
        'raise_after_second_request')
    with self.AssertRaisesToolExceptionMatches('raise_after_second_request'):
      self.Run("""
          compute instances tail-serial-port-output instance-1
            --zone central2-a --port 4
          """)

    self.CheckRequests(
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              port=4,
              zone='central2-a'))],
        [(self.compute.instances,
          'GetSerialPortOutput',
          self.messages.ComputeInstancesGetSerialPortOutputRequest(
              instance='instance-1',
              project='my-project',
              port=4,
              start=len(CONTENTS),
              zone='central2-a'))],
    )
    self.AssertOutputEquals(CONTENTS)

  def testWithInvalidLowPort(self):
    with self.AssertRaisesArgumentErrorRegexp(
        ('argument --port: Value must be greater than or equal to 1; '
         'received: 0')):
      self.Run("""
          compute instances tail-serial-port-output instance-1
            --zone central2-a --port 0
          """)

  def testWithInvalidHighPort(self):
    with self.AssertRaisesArgumentErrorRegexp(
        ('argument --port: Value must be less than or equal to 4; '
         'received: 5')):
      self.Run("""
          compute instances tail-serial-port-output instance-1
            --zone central2-a --port 5
          """)


if __name__ == '__main__':
  test_case.main()
