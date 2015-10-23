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
    """Create a subnet.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_ADDRESS_KEY, 
                                 ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    virtual_network_name = azure_config[constants.VIRTUAL_NETWORK_KEY]
    # virtual_network_name = utils.get_target_property(
    #                                     ctx,
    #                                     constants.SUBNET_CONNECTED_TO_NETWORK,
    #                                     constants.VIRTUAL_NETWORK_KEY
    #                                     )
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

    try:
        ctx.logger.debug("Search for an security_group")
        security_group_id = utils.get_target_property(ctx,
            constants.SUBNET_CONNECTED_TO_SECURITY_GROUP,
            constants.SECURITY_GROUP_ID_KEY
        )
        ctx.logger.debug("security_group found: {}".format(security_group_id))
        json['properties']['networkSecurityGroup']={'id': str(security_group_id)}
    except:
        ctx.logger.debug('Subnet not connected to a security group')
        pass

    ctx.logger.debug('JSON: {}'.format(json))

    response = connection.AzureConnectionClient().azure_put(ctx,
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
    """Delete a subnet.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
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


def get_provisioning_state(**_):
    """Get the provisioning state of a subnet.

    :param ctx: The Cloudify ctx context.
    :return: The provisioning state of a subnet.
    :rtype: string
    """
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
    """Get the id of a subnet (relationship function for a network interface card).

    :param ctx: The Cloudify ctx context.
    :return: The id of a subnet.
    :rtype: string
    """
    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]

    api_version = constants.AZURE_API_VERSION_05_preview
    virtual_network_name = azure_config[constants.VIRTUAL_NETWORK_KEY]
    subnet_name = azure_config[constants.SUBNET_KEY]

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

def get_json_from_azure(**_):
    """Get the json of a subnet.

    :param ctx: The Cloudify ctx context.
    :return: The json of a subnet.
    :rtype: dictionary
    """
    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]

    api_version = constants.AZURE_API_VERSION_05_preview
    virtual_network_name = utils.get_target_property(ctx,
        constants.SUBNET_CONNECTED_TO_NETWORK,
        constants.VIRTUAL_NETWORK_KEY
    )
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]

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

    return response.json()
