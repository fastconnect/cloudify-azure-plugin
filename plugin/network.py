# -*- coding: utf-8 -*-
########
# Copyright (c) 2015 Fastconnect - Atost. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from plugin import (utils,
                    constants,
                    connection,
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


@operation
def create(**_):
    """Create a virtual network.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.VIRTUAL_NETWORK_ADDRESS_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    virtual_network_address_prefix = ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    
    # Place the network name in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] = \
        ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]

    list = get_list_networks(ctx=ctx)
    if len(list)>0:
        ctx.logger.debug('virtual net name: {}'.format(virtual_network_name))
        ctx.logger.debug('virtual net address: {}'.format(virtual_network_address_prefix))
        for net in list:
            name = net['name']
            address = net['properties']['addressSpace']['addressPrefixes'][0]
            ctx.logger.debug('found net name: {}'.format(str(name)))
            if str(name) == virtual_network_name:
                ctx.logger.debug('found net address: {}'\
                    .format(str(address))
                )
                if str(address) == virtual_network_address_prefix:
                    ctx.logger.warning('Reuse already existing Virtual Network')
                    return 202
                else:
                    raise NonRecoverableError('Virtual Network already exist with an other address prefix')

    json ={
        "location": str(location),
        "properties":{
            "addressSpace":{
                "addressPrefixes":[
                    str(virtual_network_address_prefix)
                ]
            }
        }
    }

    ctx.logger.info('Creating Virtual Network')
    connect = connection.AzureConnectionClient()

    response = connect.azure_put(ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
            "providers/microsoft.network" +
            "/virtualNetworks/{}" +
            "?api-version={}").format(
            subscription_id,
            resource_group_name,
            virtual_network_name,
            api_version
        ),
        json=json
    )
    return response.status_code


@operation
def delete(**_):
    """Delete a virtual network.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    deletable = ctx.node.properties[constants.DELETABLE_KEY]

    if deletable:
        ctx.logger.info('Propertie deletable set to True.')
        ctx.logger.info('Deleting virtual network {}.'.format(virtual_network_name))

        connect = connection.AzureConnectionClient()

        response = connect.azure_delete(ctx,
            ("subscriptions/{}/resourceGroups/{}/" +
                "providers/microsoft.network" +
                "/virtualNetworks/{}" +
                "?api-version={}").format(
                subscription_id,
                resource_group_name,
                virtual_network_name,
                api_version
            )
        )
        return response.status_code

    else:
        ctx.logger.info('Propertie deletable set to False.')
        ctx.logger.info('Not deleting virtual network {}.'.format(virtual_network_name))
        return 0


def get_provisioning_state(**_):
    """Get the provisioning state of a virtual network.

    :param ctx: The Cloudify ctx context.
    :return: The provisioning state of a virtual network.
    :rtype: string
    """
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    connect = connection.AzureConnectionClient()

    response = connect.azure_get(ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
            "providers/microsoft.network" +
            "/virtualNetworks/{}" +
            "?api-version={}").format(
            subscription_id,
            resource_group_name,
            virtual_network_name,
            api_version
        )
    )

    jsonGet = response.json()
    status_storage = jsonGet['properties']['provisioningState']

    return status_storage

def get_list_networks(**_):
    """Get the list of all virtual networks in the resource group.

    :param ctx: The Cloudify ctx context.
    :return: The list of all virtual networks.
    :rtype: table
    """
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    connect = connection.AzureConnectionClient()

    response = connect.azure_get(ctx,
        ("subscriptions/{}" +
         "/resourceGroups/{}"
         "/providers/microsoft.network" +
         "/virtualnetworks" +
         "?api-version={}").format(
            subscription_id,
            resource_group_name,
            api_version
        )
    )

    ctx.logger.debug(response.json()['value'])
    return response.json()['value']
