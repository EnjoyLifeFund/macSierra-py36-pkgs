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


class KeyVaultSecretReference(Model):
    """Describes a reference to Key Vault Secret.

    :param secret_url: The URL referencing a secret in a Key Vault.
    :type secret_url: str
    :param source_vault: The relative URL of the Key Vault containing the
     secret.
    :type source_vault: :class:`SubResource
     <azure.mgmt.compute.compute.v2016_04_30_preview.models.SubResource>`
    """

    _validation = {
        'secret_url': {'required': True},
        'source_vault': {'required': True},
    }

    _attribute_map = {
        'secret_url': {'key': 'secretUrl', 'type': 'str'},
        'source_vault': {'key': 'sourceVault', 'type': 'SubResource'},
    }

    def __init__(self, secret_url, source_vault):
        self.secret_url = secret_url
        self.source_vault = source_vault
