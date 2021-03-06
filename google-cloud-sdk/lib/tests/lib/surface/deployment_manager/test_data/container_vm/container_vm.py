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

#% description: Creates a Container VM with the provided Container manifest.
#% parameters:
#% - name: zone
#%   type: string
#%   description: Zone in which this VM will run
#%   required: true
#% - name: containerImage
#%   type: string
#%   description: Name of the Google Cloud Container VM Image
#%     (e.g., container-vm-v20150317).
#%   required: true
#% - name: containerManifest
#%   type: string
#%   description: String containing the Container Manifest in YAML
#%   required: true

"""Creates a Container VM with the provided Container manifest.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


def GenerateConfig(context):
  return """
resources:
  - type: compute.v1.instance
    name: {name}
    properties:
      zone: {zone}
      machineType: https://www.googleapis.com/compute/v1/projects/{project}/zones/{zone}/machineTypes/n1-standard-1
      metadata:
        items:
          - key: google-container-manifest
            value: "{manifest}"
      disks:
        - deviceName: boot
          type: PERSISTENT
          boot: true
          autoDelete: true
          initializeParams:
            diskName: {name}-disk
            sourceImage: https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/family/{containerImage}
      networkInterfaces:
        - accessConfigs:
            - name: external-nat
              type: ONE_TO_ONE_NAT
          network: https://www.googleapis.com/compute/v1/projects/{project}/global/networks/default
""".format(name=context.env["name"] + "-" + context.env["deployment"],
           project=context.env["project"],
           zone=context.properties["zone"],
           containerImage=context.properties["containerImage"],
           manifest=context.properties["containerManifest"])
