import connection
import constants
import utils

from cloudify import ctx


def create_network(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('virtual_network_name', ctx.node.properties)
    utils.validate_node_property('location', ctx.node.properties)
    utils.validate_node_property('virtual_network_address_prefix', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    virtual_network_name = ctx.node.properties['virtual_network_name']
    location = ctx.node.properties['location']
    virtual_network_address_prefix = ctx.node.properties['virtual_network_address_prefix']
    api_version = constants.AZURE_API_VERSION_05_preview

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


def delete_network(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('virtual_network_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    virtual_network_name = ctx.node.properties['virtual_network_name']
    api_version = constants.AZURE_API_VERSION_05_preview

    ctx.logger.info('Deleting Virtual Network')
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


def get_provisioning_state_network(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('virtual_network_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    virtual_network_name = ctx.node.properties['virtual_network_name']
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


def create_subnet(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('virtual_network_name', ctx.node.properties)
    utils.validate_node_property('subnet_name', ctx.node.properties)
    utils.validate_node_property('subnet_address_prefix', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    virtual_network_name = ctx.node.properties['virtual_network_name']
    subnet_name = ctx.node.properties['subnet_name']
    subnet_address_prefix = ctx.node.properties['subnet_address_prefix']
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


def delete_subnet(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('virtual_network_name', ctx.node.properties)
    utils.validate_node_property('subnet_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    virtual_network_name = ctx.node.properties['virtual_network_name']
    subnet_name = ctx.node.properties['subnet_name']
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


def get_provisioning_state_subnet(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('virtual_network_name', ctx.node.properties)
    utils.validate_node_property('subnet_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    virtual_network_name = ctx.node.properties['virtual_network_name']
    subnet_name = ctx.node.properties['subnet_name']
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