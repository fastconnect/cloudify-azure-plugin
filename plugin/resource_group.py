# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )

from cloudify import ctx
from cloudify.decorators import operation

def get_provisioning_state(**_):
    utils.validate_node_property(constants.RESOURCE_GROUP_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    api_version = str(constants.AZURE_API_VERSION_04_PREVIEW)
    resource_group_name = ctx.node.properties[constants.RESOURCE_GROUP_KEY]

    response = connection.AzureConnectionClient().azure_get(
            ctx, 
            ("subscriptions/{}/resourcegroups/"+
            "{}?api-version={}").format(
                subscription_id, 
                resource_group_name, 
                api_version
            )
        )
    jsonGet = response.json()
    status_resource_group = jsonGet['properties']['provisioningState']
    return status_resource_group


@operation
def delete(**_):
    utils.validate_node_property(constants.RESOURCE_GROUP_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    api_version = constants.AZURE_API_VERSION_04_PREVIEW
    resource_group_name = ctx.node.properties[constants.RESOURCE_GROUP_KEY]
    deletable = ctx.node.properties[constants.DELETABLE_KEY]
    
    if deletable:
        ctx.logger.info('Propertie deletable set to True.')
        ctx.logger.info('Deleting resource group {}.'.format(resource_group_name))
        cntn = connection.AzureConnectionClient()
        response = cntn.azure_delete(ctx, 
                       ("subscriptions/{}/resourcegroups/{}" +
                        "?api-version={}").format(
                                                subscription_id, 
                                                resource_group_name, 
                                                api_version
                                                )
                        )
        return response.status_code

    else:
        ctx.logger.info('Propertie deletable set to False.')
        ctx.logger.info('Not deleting resource group {}.'.format(resource_group_name))
        return 0

@operation
def create(**_):
    utils.validate_node_property(constants.RESOURCE_GROUP_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)
    
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_04_PREVIEW
    resource_group_name = ctx.node.properties[constants.RESOURCE_GROUP_KEY]

    json ={"location": str(location)}

    ctx.logger.info('Beginning resource_group creation')
    cntn = connection.AzureConnectionClient()

    response = cntn.azure_put(ctx, 
                   ("subscriptions/{}/resourcegroups/{}" +
                    "?api-version={}").format(
                                            subscription_id, 
                                            resource_group_name, 
                                            api_version
                                            ),
                    json=json
                    )
    return response.status_code
