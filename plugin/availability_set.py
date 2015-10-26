# -*- coding: utf-8 -*-
from plugin import (connection,
                    constants,
                    utils
                    )

from cloudify import ctx
from cloudify.decorators import operation


def get_provisioning_state(**_):
    """
    Get provisioning state of the availability set.

    :return: The string of the status (Creating, Updating, Failed, Succeeded or Deleting).
    :rtype: string
    """
    utils.validate_node_property(constants.AVAILABILITY_SET_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    availability_set_name = ctx.instance.runtime_properties[constants.AVAILABILITY_SET_KEY]

    response = connection.AzureConnectionClient().azure_get(ctx,
        ("subscriptions/{}"
         "/resourceGroups/{}"
         "/providers/Microsoft.Compute"
         "/availabilitySets/{}"
         "?api-version={}").format(
            subscription_id,
            resource_group_name,
            availability_set_name,
            api_version
        )
    )

    if response.status_code == 200:
        return constants.SUCCEEDED
    else:
        return 'Executing'


@operation
def delete(**_):
    """
    Delete the availability set.

    :return: The int of the status code of the request (200 OK; 404 Not Found).
    :rtype: int
    """
    utils.validate_node_property(constants.AVAILABILITY_SET_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    availability_set_name = ctx.node.properties[constants.AVAILABILITY_SET_KEY]

    deletable = ctx.node.properties[constants.DELETABLE_KEY]

    if deletable:
        ctx.logger.info('Properties deletable set to True.')
        ctx.logger.info('Deleting availability set {}.'.format(availability_set_name))
        response = connection.AzureConnectionClient().azure_delete(ctx,
            ("subscriptions/{}" +
             "/resourceGroups/{}" +
             "/providers/Microsoft.Compute" +
             "/availabilitySets/{}" +
             "?api-version={}").format(subscription_id,
                resource_group_name,
                availability_set_name,
                api_version
            )
        )
        return response.status_code
    else:
        ctx.logger.info('Properties deletable set to False.')
        ctx.logger.info('Not deleting availability set {}.'.format(availability_set_name))
        return 0


@operation
def create(**_):
    """
    Create the availability set.

    :return: The int of the status code of the request (200 OK; 404 Not Found).
    :rtype: int
    """
    utils.validate_node_property(constants.AVAILABILITY_SET_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    availability_set_name = ctx.node.properties[constants.AVAILABILITY_SET_KEY]

    # Place the availability_set name in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.AVAILABILITY_SET_KEY] = \
        availability_set_name

    json ={
        "name": str(availability_set_name),
        "type": "Microsoft.Compute/availabilitySets",
        "location": str(location),
        "properties": {
            "platformUpdateDomainCount": 5,
            "platformFaultDomainCount": 3
        }
    }

    response = connection.AzureConnectionClient().azure_put(ctx,
        ("subscriptions/{}" +
         "/resourceGroups/{}" +
         "/providers/Microsoft.Compute" +
         "/availabilitySets/{}" +
         "?api-version={}").format(
            subscription_id,
            resource_group_name,
            availability_set_name,
            api_version
        ),
        json=json
    )

    # Place the availability_set id in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.AVAILABILITY_ID_KEY] = \
        response.json()['id']

    utils.wait_status(ctx, 'availability_set')

    return response.status_code


def get_id(**_):
    """
    Relationship function:
        Get the id of the availability set.

    :return: The string of the availability set id's.
    :rtype: string
    """
    return ctx.target.instance.runtime_properties[constants.AVAILABILITY_ID_KEY]
