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

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = utils.get_target_property(
                                        ctx, 
                                        constants.SUBNET_CONNECTED_TO_NETWORK,
                                        constants.VIRTUAL_NETWORK_KEY
                                        )
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]
    subnet_address_prefix = ctx.node.properties[constants.SUBNET_ADDRESS_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    # Place the network name in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] = \
        virtual_network_name
    ctx.instance.runtime_properties[constants.SUBNET_KEY] = \
        subnet_name

    json = {
        "properties": {
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

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = utils.get_target_property(
                                        ctx, 
                                        constants.SUBNET_CONNECTED_TO_NETWORK,
                                        constants.VIRTUAL_NETWORK_KEY
                                        )
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


def get_provisioning_state(**_):
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = utils.get_target_property(
                                        ctx, 
                                        constants.SUBNET_CONNECTED_TO_NETWORK,
                                        constants.VIRTUAL_NETWORK_KEY
                                        )
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


def get_id(**_):
    # get the subnet id for the nic relationship
    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]

    api_version = constants.AZURE_API_VERSION_05_preview
    virtual_network_name = utils.get_target_property(
        ctx,
        constants.NIC_CONNECTED_TO_SUBNET,
        constants.VIRTUAL_NETWORK_KEY
    )
    subnet_name = utils.get_target_property(
        ctx,
        constants.NIC_CONNECTED_TO_SUBNET,
        constants.SUBNET_KEY
    )

    response = connection.AzureConnectionClient().azure_get(
        ctx,
        ('subscriptions/{}' +
         '/resourceGroups/{}' +
         '/providers/microsoft.network' +
         '/virtualNetworks/{}' +
         '/subnets/{}' +
         '?api-version={}').format(
            subscription_id,
            resource_group_name,
            virtual_network_name,
            subnet_name,
            api_version
        )
    )
    return response.json()['id']
