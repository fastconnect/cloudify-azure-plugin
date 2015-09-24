# -*- coding: utf-8 -*-
from plugin import (connection,
                    constants,
                    utils
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


def get_provisioning_state(**_):
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
    return response.status_code


def get_id(ctx):
    # get the public_id for the nic relationship
    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    public_ip_name = utils.get_target_property(
        ctx,
        constants.NIC_CONNECTED_TO_PUBLIC_IP,
        constants.PUBLIC_IP_KEY
    )

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
