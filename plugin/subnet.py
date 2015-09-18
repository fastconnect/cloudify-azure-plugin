# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    network
                    )

from cloudify import ctx
from cloudify.decorators import operation

@operation
def create(**_):
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_ADDRESS_KEY, 
                                 ctx.node.properties)
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, 
                                 ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.instance.runtime_properties[
                                    constants.VIRTUAL_NETWORK_KEY]
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
def delete(**_):
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, 
                                 ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.instance.runtime_properties[
                                            constants.VIRTUAL_NETWORK_KEY]
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    ctx.logger.info('Deleting Subnet')
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

@operation
def preconfigure_subnet_connected_to_network(**_):
    # Add the virtual network name to subnet's runtime properties
    ctx.source.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] = \
        ctx.target.node.properties[constants.VIRTUAL_NETWORK_KEY]


def get_provisioning_state(**_):
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, 
                                 ctx.instance.runtime_properties)
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = ctx.instance.runtime_properties[
                                            constants.VIRTUAL_NETWORK_KEY]
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