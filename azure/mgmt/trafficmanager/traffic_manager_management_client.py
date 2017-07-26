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

from msrest.service_client import ServiceClient
from msrest import Serializer, Deserializer
from msrestazure import AzureConfiguration
from .version import VERSION
from .operations.endpoints_operations import EndpointsOperations
from .operations.profiles_operations import ProfilesOperations
from .operations.geographic_hierarchies_operations import GeographicHierarchiesOperations
from . import models


class TrafficManagerManagementClientConfiguration(AzureConfiguration):
    """Configuration for TrafficManagerManagementClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(TrafficManagerManagementClientConfiguration, self).__init__(base_url)

        self.add_user_agent('trafficmanagermanagementclient/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id


class TrafficManagerManagementClient(object):
    """TrafficManagerManagementClient

    :ivar config: Configuration for client.
    :vartype config: TrafficManagerManagementClientConfiguration

    :ivar endpoints: Endpoints operations
    :vartype endpoints: azure.mgmt.trafficmanager.operations.EndpointsOperations
    :ivar profiles: Profiles operations
    :vartype profiles: azure.mgmt.trafficmanager.operations.ProfilesOperations
    :ivar geographic_hierarchies: GeographicHierarchies operations
    :vartype geographic_hierarchies: azure.mgmt.trafficmanager.operations.GeographicHierarchiesOperations

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, base_url=None):

        self.config = TrafficManagerManagementClientConfiguration(credentials, subscription_id, base_url)
        self._client = ServiceClient(self.config.credentials, self.config)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self.api_version = '2017-05-01'
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

        self.endpoints = EndpointsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.profiles = ProfilesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.geographic_hierarchies = GeographicHierarchiesOperations(
            self._client, self.config, self._serialize, self._deserialize)