from cloudify.decorators import operation
import connection
import constants
import utils

from cloudify import ctx
from cloudify.decorators import operation


@operation
def create(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('storage_account_name', ctx.node.properties)
    utils.validate_node_property('location', ctx.node.properties)
    utils.validate_node_property('account_type', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    storage_account_name = ctx.node.properties['storage_account_name']
    location = ctx.node.properties['location']
    account_type = ctx.node.properties['account_type']
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
    return response.status_code


@operation
def delete(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('storage_account_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    storage_account_name = ctx.node.properties['storage_account_name']
    api_version = constants.AZURE_API_VERSION_05_preview

    ctx.logger.info('Deleting Storage Account')
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


def get_provisioning_state(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('storage_account_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    storage_account_name = ctx.node.properties['storage_account_name']
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
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('storage_account_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    storage_account_name = ctx.node.properties['storage_account_name']
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