# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )

from cloudify import ctx
from cloudify.decorators import operation


@operation
def create_network(**_):
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.VIRTUAL_NETWORK_ADDRESS_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    virtual_network_address_prefix = ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

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
def delete_network(**_):
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


def get_provisioning_state_network(**_):
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


@operation
def create_subnet(**_):
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_ADDRESS_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]
    subnet_address_prefix = ctx.node.properties[constants.SUBNET_ADDRESS_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    json ={
       "properties":{
          "addressPrefix": str(subnet_address_prefix)
       }
    }

    ctx.logger.info('Creating Subnet')
    connect = connection.AzureConnectionClient()

    response = connect.azure_put(ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
            "providers/microsoft.network" +
            "/virtualNetworks/{}" +
            "/subnets/{}" +
            "?api-version={}").format(
            subscription_id,
            resource_group_name,
            virtual_network_name,
            subnet_name,
            api_version
        ),
        json=json
    )
    return response.status_code


@operation
def delete_subnet(**_):
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    deletable = ctx.node.properties[constants.DELETABLE_KEY]
    
    if deletable:
        ctx.logger.info('Propertie deletable set to True.')
        ctx.logger.info('Deleting subnet {}.'.format(subnet_name))

        connect = connection.AzureConnectionClient()
        response = connect.azure_delete(ctx,
            ("subscriptions/{}/resourceGroups/{}/" +
                "providers/microsoft.network" +
                "/virtualNetworks/{}" +
                "/subnets/{}" +
                "?api-version={}").format(
                subscription_id,
                resource_group_name,
                virtual_network_name,
                subnet_name,
                api_version
            )
        )
        return response.status_code
    else:
        ctx.logger.info('Propertie deletable set to False.')
        ctx.logger.info('Not deleting subnet {}.'.format(subnet_name))
        return 0
  

def get_provisioning_state_subnet(**_):
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    connect = connection.AzureConnectionClient()

    response = connect.azure_get(ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
            "providers/microsoft.network" +
            "/virtualNetworks/{}" +
            "/subnets/{}" +
            "?api-version={}").format(
            subscription_id,
            resource_group_name,
            virtual_network_name,
            subnet_name,
            api_version
        )
    )

    jsonGet = response.json()
    status_storage = jsonGet['properties']['provisioningState']

    return status_storage