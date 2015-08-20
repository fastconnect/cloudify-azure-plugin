from cloudify.exceptions import NonRecoverableError
import connection
import constants
import utils

from cloudify import ctx
from cloudify.decorators import operation

def get_public_ip_provisioning_state(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('public_ip_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    public_ip_name = ctx.node.properties['public_ip_name']

    response = connection.AzureConnectionClient().azure_get(
            ctx, 
            ("subscriptions/{}/resourcegroups/{}/"+
            "providers/microsoft.network/publicIPAddresses"+
            "/{}?api-version={}").format(
                subscription_id, 
                resource_group_name, 
                public_ip_name,
                api_version
            )
        )
    jsonGet = response.json()
    status_public_ip = jsonGet['properties']['provisioningState']
    return status_public_ip

def delete(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.node.properties)
    utils.validate_node_property('public_ip_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    network_interface_name = ctx.node.properties['network_interface_name']
    public_ip_name =ctx.node.properties['public_ip_name']

    response = connection.AzureConnectionClient().azure_delete(
      ctx, 
      ("subscriptions/{}/resourceGroups/{}/providers/microsoft.network" + 
      "/publicIPAddresses/{}?api-version={}").format(subscription_id, 
                                                    resource_group_name, 
                                                    public_ip_name, 
                                                    api_version
                                                    )
      )
    return response.status_code


def create(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('location', ctx.node.properties)
    utils.validate_node_property('public_ip_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    location = ctx.node.properties['location']
    public_ip_name = ctx.node.properties['public_ip_name']
    public_ip_allocation_method = "Static"

    json ={
       "location": str(location),
       "properties": {
            "publicIPAllocationMethod": str(public_ip_allocation_method)
            }
        }

    ctx.logger.info('Beginning public_ip creation')
    cntn = connection.AzureConnectionClient()

    response = cntn.azure_put(ctx, 
                   ("subscriptions/{}/resourcegroups/{}/" +
                    "providers/microsoft.network" +
                    "/publicIPAddresses/{}" +
                    "?api-version={}").format(
                                            subscription_id, 
                                            resource_group_name, 
                                            public_ip_name, 
                                            api_version
                                            ),
                    json=json
                    )
    return response.status_code
