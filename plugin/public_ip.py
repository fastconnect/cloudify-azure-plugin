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

from plugin import (connection,
                    constants,
                    utils
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


def get_provisioning_state(**_):
    """Get the provisioning state of a public ip.

    :param ctx: The Cloudify ctx context.
    :return: The provisioning state of a public ip.
    :rtype: string
    """
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    public_ip_name = ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY]

    response = connection.AzureConnectionClient().azure_get(
            ctx, 
            ("subscriptions/{}/resourcegroups/{}/"+
            "providers/microsoft.network/publicIPAddresses"+
            "/{}?api-version={}").format(
                subscription_id, 
                resource_group_name, 
                public_ip_name,
                api_version
            )
        )
    jsonGet = response.json()
    status_public_ip = jsonGet['properties']['provisioningState']
    return status_public_ip


@operation
def delete(**_):
    """Delete a public ip.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    public_ip_name =ctx.node.properties[constants.PUBLIC_IP_KEY]

    deletable = ctx.node.properties[constants.DELETABLE_KEY]
    
    if deletable:
        ctx.logger.info('Propertie deletable set to True.')
        ctx.logger.info('Deleting public ip {}.'.format(public_ip_name))
        response = connection.AzureConnectionClient().azure_delete(
        ctx, 
        ("subscriptions/{}/resourceGroups/{}/providers/microsoft.network" + 
        "/publicIPAddresses/{}?api-version={}").format(subscription_id, 
                                                    resource_group_name, 
                                                    public_ip_name, 
                                                    api_version
                                                    )
        )
        return response.status_code
    else:
        ctx.logger.info('Propertie deletable set to False.')
        ctx.logger.info('Not deleting public ip {}.'.format(public_ip_name))
        return 0


@operation
def create(**_):
    """Create a public ip.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_06
    public_ip_name = ctx.node.properties[constants.PUBLIC_IP_KEY] 
    public_ip_allocation_method = "Dynamic"

    # Place the public_ip name in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = \
        public_ip_name
    
    json ={
       "location": str(location),
       "properties": {
            "publicIPAllocationMethod": str(public_ip_allocation_method)
            }
        }

    cntn = connection.AzureConnectionClient()

    response = cntn.azure_put(ctx, 
                   ("subscriptions/{}/resourcegroups/{}/" +
                    "providers/microsoft.network" +
                    "/publicIPAddresses/{}" +
                    "?api-version={}").format(
                                            subscription_id, 
                                            resource_group_name, 
                                            public_ip_name, 
                                            api_version
                                            ),
                    json=json
                    )

    utils.wait_status(ctx, 'public_ip')

    return response.status_code


def get_id(**_):
    """Get the id of a public ip (relationship function for a network interface card).

    :param ctx: The Cloudify ctx context.
    :return: The id of a public ip.
    :rtype: string
    """
    # get the public_id for the nic relationship
    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    public_ip_name = ctx.target.node.properties[constants.PUBLIC_IP_KEY]

    response = connection.AzureConnectionClient().azure_get(
                              ctx, 
                              ('subscriptions/{}' +
                              '/resourceGroups/{}' +
                              '/providers/microsoft.network/' +
                              'publicIPAddresses/{}' +
                              '?api-version={}').format(
                                  subscription_id,
                                  resource_group_name,
                                  public_ip_name,
                                  api_version
                                  )
                              )

    return response.json()['id']
