# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )

from cloudify import ctx
from cloudify.decorators import operation


def get_provisioning_state(**_):
    """Get the provisioning state of a security group.

    :param ctx: The Cloudify ctx context.
    :return: The provisioning state of a security group.
    :rtype: string
    """
    utils.validate_node_property(constants.SECURITY_GROUP_KEY, ctx.node.properties)
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    security_group_name = ctx.node.properties[constants.SECURITY_GROUP_KEY]

    response = connection.AzureConnectionClient().azure_get(ctx,
        ("subscriptions/{}"
         "/resourceGroups/{}"
         "/providers/microsoft.network"
         "/networkSecurityGroups/{}"
         "?api-version={}").format(
            subscription_id,
            resource_group_name,
            security_group_name,
            api_version
        )
    )

    jsonGet = response.json()
    status_resource_group = jsonGet['properties']['provisioningState']
    return status_resource_group


@operation
def delete(**_):
    """Delete a security group.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.SECURITY_GROUP_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    security_group_name = ctx.node.properties[constants.SECURITY_GROUP_KEY]
    deletable = ctx.node.properties[constants.DELETABLE_KEY]

    if deletable:
        ctx.logger.info('Properties deletable set to True.')
        ctx.logger.info('Deleting security group {}.'.format(security_group_name))
        response = connection.AzureConnectionClient().azure_delete(ctx,
            ("subscriptions/{}" +
             "/resourceGroups/{}" +
             "/providers/microsoft.network" +
             "/networkSecurityGroups/{}" +
             "?api-version={}").format(subscription_id,
                resource_group_name,
                security_group_name,
                api_version
            )
        )
        return response.status_code

    else:
        ctx.logger.info('Properties deletable set to False.')
        ctx.logger.info('Not deleting security group {}.'.format(security_group_name))
        return 0

@operation
def create(**_):
    """Create a security group.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.SECURITY_GROUP_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    security_group_name = ctx.node.properties[constants.SECURITY_GROUP_KEY]
    rules = ctx.node.properties[constants.RULES_KEY]

    json_secu = {
        "location": str(location),
        "properties":{
            "securityRules":[]
        }
    }

    n_priority = 1
    for rule in rules:
        priority = n_priority*100

        protocol = str(rule[constants.PROTOCOL_KEY])\
            if constants.PROTOCOL_KEY in rule else "*"
        sourcePort = str(rule[constants.SOURCE_PORT_KEY])\
            if constants.SOURCE_PORT_KEY in rule else "*"
        destinationPort = str(rule[constants.DEST_PORT_KEY])\
            if constants.DEST_PORT_KEY in rule else "*"
        sourceAddress = str(rule[constants.SOURCE_ADDRESS_KEY])\
            if constants.SOURCE_ADDRESS_KEY in rule else "*"
        destinationAddress = str(rule[constants.DEST_ADDRESS_KEY])\
            if constants.DEST_ADDRESS_KEY in rule else "*"
        access = str(rule[constants.ACCESS_KEY])\
            if constants.ACCESS_KEY in rule else "Allow"
        direction = str(rule[constants.DIRECTION_KEY])\
            if constants.DIRECTION_KEY in rule else "Inbound"

        json_rule = {
            "name": str(rule[constants.RULE_KEY]),
            "properties":{
                "protocol": protocol,
                "sourcePortRange": sourcePort,
                "destinationPortRange": destinationPort,
                "sourceAddressPrefix": sourceAddress,
                "destinationAddressPrefix": destinationAddress,
                "access": access,
                "priority": priority,
                "direction": direction
            }
        }

        json_secu['properties']['securityRules'].append(json_rule)
        n_priority+=1

    response = connection.AzureConnectionClient().azure_put(ctx,
        ("subscriptions/{}" +
         "/resourceGroups/{}" +
         "/providers/microsoft.network" +
         "/networkSecurityGroups/{}" +
         "?api-version={}").format(
            subscription_id,
            resource_group_name,
            security_group_name,
            api_version
        ),
        json=json_secu
    )

    # Place the availability_set id in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.SECURITY_GROUP_ID_KEY] = \
        response.json()['id']

    return response.status_code
