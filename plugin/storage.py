# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )

from cloudify import ctx
from cloudify.decorators import operation


@operation
def create(**_):
    utils.validate_node_property(constants.STORAGE_ACCOUNT_KEY, ctx.node.properties)
    utils.validate_node_property(constants.ACCOUNT_TYPE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    storage_account_name = ctx.node.properties[constants.STORAGE_ACCOUNT_KEY]
    account_type = ctx.node.properties[constants.ACCOUNT_TYPE_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    ctx.logger.info('Checking availability storage_account_name ' + str(storage_account_name))
    availability = availability_account_name(ctx=ctx)

    if (not bool(availability['nameAvailable'])):
        if (availability['reason'] == 'AlreadyExists'):
            ctx.logger.info("storage_account_name " + str(storage_account_name) + " already exist")
            ctx.logger.info(str(availability['message']))
            return 409
        elif (availability['reason'] == 'Invalid'):
            ctx.logger.info("storage_account_name " + str(storage_account_name) + " invalid name")
            ctx.logger.info(str(availability['message']))
            return 400

    # Place the storage name in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.STORAGE_ACCOUNT_KEY] = storage_account_name

    json ={
        "location": str(location),
        "properties": {
            "accountType": str(account_type)
        }
    }

    ctx.logger.info('Creating Storage Account')
    connect = connection.AzureConnectionClient()

    response = connect.azure_put(ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
            "providers/Microsoft.Storage" +
            "/storageAccounts/{}" +
            "?api-version={}").format(
            subscription_id,
            resource_group_name,
            storage_account_name,
            api_version
        ),
        json=json
    )

    utils.wait_status(ctx, 'storage')

    return response.status_code


@operation
def delete(**_):
    utils.validate_node_property(constants.STORAGE_ACCOUNT_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    storage_account_name = ctx.node.properties[constants.STORAGE_ACCOUNT_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    deletable = ctx.node.properties[constants.DELETABLE_KEY]

    if deletable:
        ctx.logger.info('Propertie deletable set to True.')
        ctx.logger.info('Deleting Storage Account {}.'.format(storage_account_name))
        connect = connection.AzureConnectionClient()

        response = connect.azure_delete(ctx,
            ("subscriptions/{}/resourceGroups/{}/" +
                "providers/Microsoft.Storage" +
                "/storageAccounts/{}" +
                "?api-version={}").format(
                subscription_id,
                resource_group_name,
                storage_account_name,
                api_version
            )
        )
        return response.status_code
    else:
        ctx.logger.info('Propertie deletable set to False.')
        ctx.logger.info('Not deleting storage account {}.'.format(storage_account_name))
        return 0
    


def get_provisioning_state(**_):
    utils.validate_node_property(constants.STORAGE_ACCOUNT_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    storage_account_name = ctx.node.properties[constants.STORAGE_ACCOUNT_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    connect = connection.AzureConnectionClient()

    response = connect.azure_get(ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
            "providers/Microsoft.Storage" +
            "/storageAccounts/{}" +
            "?api-version={}").format(
            subscription_id,
            resource_group_name,
            storage_account_name,
            api_version
        )
    )

    jsonGet = response.json()
    status_storage = jsonGet['properties']['provisioningState']

    return status_storage


def availability_account_name(**_):
    utils.validate_node_property(constants.STORAGE_ACCOUNT_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    storage_account_name = ctx.node.properties[constants.STORAGE_ACCOUNT_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    json ={
        "name": str(storage_account_name),
        "type": "Microsoft.Storage/storageAccounts"
    }

    connect = connection.AzureConnectionClient()

    response = connect.azure_post(ctx,
        ("subscriptions/{}/" +
            "providers/Microsoft.Storage" +
            "/checkNameAvailability" +
            "?api-version={}").format(
            subscription_id,
            api_version
        ),
        json=json
    )

    return response.json()