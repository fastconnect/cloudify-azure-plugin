# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


@operation
def create(**_):
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


@operation
def get_provisioning_state(**_):
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
