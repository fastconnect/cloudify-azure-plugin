# -*- coding: utf-8 -*-
import connection
import constants
import utils

from cloudify import ctx
from cloudify.decorators import operation

def get_ressource_group_provisioning_state(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = str(constants.AZURE_API_VERSION_04_PREVIEW)
    resource_group_name = ctx.node.properties['resource_group_name']

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
    status_ressource_group = jsonGet['properties']['provisioningState']
    return status_ressource_group


@operation
def delete(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_04_PREVIEW
    resource_group_name = ctx.node.properties['resource_group_name']

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


@operation
def create(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('location', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_04_PREVIEW
    resource_group_name = ctx.node.properties['resource_group_name']
    location = ctx.node.properties['location']

    json ={"location": str(location)}

    ctx.logger.info('Beginning ressource_group creation')
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
