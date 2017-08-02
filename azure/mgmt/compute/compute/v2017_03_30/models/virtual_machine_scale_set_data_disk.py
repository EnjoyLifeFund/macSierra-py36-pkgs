# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class VirtualMachineScaleSetDataDisk(Model):
    """Describes a virtual machine scale set data disk.

    :param name: The disk name.
    :type name: str
    :param lun: The logical unit number.
    :type lun: int
    :param caching: The caching type. Possible values include: 'None',
     'ReadOnly', 'ReadWrite'
    :type caching: str or :class:`CachingTypes
     <azure.mgmt.compute.compute.v2017_03_30.models.CachingTypes>`
    :param create_option: The create option. Possible values include:
     'fromImage', 'empty', 'attach'
    :type create_option: str or :class:`DiskCreateOptionTypes
     <azure.mgmt.compute.compute.v2017_03_30.models.DiskCreateOptionTypes>`
    :param disk_size_gb: The initial disk size in GB for blank data disks, and
     the new desired size for existing OS and Data disks.
    :type disk_size_gb: int
    :param managed_disk: The managed disk parameters.
    :type managed_disk: :class:`VirtualMachineScaleSetManagedDiskParameters
     <azure.mgmt.compute.compute.v2017_03_30.models.VirtualMachineScaleSetManagedDiskParameters>`
    """

    _validation = {
        'lun': {'required': True},
        'create_option': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'lun': {'key': 'lun', 'type': 'int'},
        'caching': {'key': 'caching', 'type': 'CachingTypes'},
        'create_option': {'key': 'createOption', 'type': 'DiskCreateOptionTypes'},
        'disk_size_gb': {'key': 'diskSizeGB', 'type': 'int'},
        'managed_disk': {'key': 'managedDisk', 'type': 'VirtualMachineScaleSetManagedDiskParameters'},
    }

    def __init__(self, lun, create_option, name=None, caching=None, disk_size_gb=None, managed_disk=None):
        self.name = name
        self.lun = lun
        self.caching = caching
        self.create_option = create_option
        self.disk_size_gb = disk_size_gb
        self.managed_disk = managed_disk
