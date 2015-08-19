from cloudify.exceptions import NonRecoverableError
import connection
import constants
import utils

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

def _get_vm_public_ip(ctx):
    ''' 
        Get the public IP from a machine or a network interface. 
    '''
    azure_connection = connection.AzureConnectionClient()

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties['compute_name']
    resource_group = ctx.node.properties['resource_group_name']
    nic = ctx.node.properties['network_interface_name']

    if nic is not None:
        response = azure_connection.azure_get(
                                    ctx,
                                    ("subscriptions/{}" + 
                                    "/resourceGroups/{}/providers/" + 
                                    "microsoft.network/networkInterfaces/{}"
                                    "?api-version={}"
                                    ).format(subscription_id, 
                                             resource_group, 
                                             nic,
                                             api_version
                                             )
                                    )

    elif vm_name is not None:
        response = azure_connection.azure_get(
                            ctx,
                ("subscriptions/{}" +
                "/resourceGroups/{}/providers" + 
                "/Microsoft.Compute/virtualMachines/{}?" + 
                "api-version={}").format(subscription_id,
                                                     resource_group, 
                                                     vm_name,
                                                     api_version
                                                     )
                            )
        nic_id = (response.json())(['properties']['networkProfile']
                                   ['networkInterfaces'][0]['id']
                                  )

        response = azure_connection.azure_get(
                            ctx, 
                            "{}?api-version={}".format(nic, api_version)
                            )
    else:
        raise NonRecoverableError('Unable to get public ip: missing argument')

    pip = (response.json())['properties']['ipConfigurations'][0]['properties']['publicIPAddress']['id']

    response = azure_connection.azure_get(
                                        ctx,
                                        "{}?api-version={}"
                                                        .format(pip,
                                                                api_version
                                                                )
                                        )

    return (response.json())['properties']['ipAddress']


def get_nic_provisioning_state(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    network_interface_name = ctx.node.properties['network_interface_name']
    response = connection.AzureConnectionClient().azure_get(
            ctx, 
            ("subscriptions/{}/resourcegroups/{}/"+
            "providers/microsoft.network/networkInterfaces"+
            "/{}?InstanceView&api-version={}").format(
                subscription_id, 
                resource_group_name, 
                network_interface_name,
                api_version
            )
        )
    jsonGet = response.json()
    status_nic = jsonGet['properties']['provisioningState']
    return status_nic


def create(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('location', ctx.node.properties)
    utils.validate_node_property('management_network_name', ctx.node.properties)
    utils.validate_node_property('management_subnet_name', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.node.properties)
    utils.validate_node_property('ip_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    location = ctx.node.properties['location']
    management_network_name = ctx.node.properties['management_network_name']
    management_subnet_name = ctx.node.properties['management_subnet_name']
    network_interface_name = ctx.node.properties['network_interface_name']
    ip_name = ctx.node.properties['ip_name']
    private_ip_allocation_method = "Dynamic"

    json ={
        "location": str(location),
        "properties": {
            "ipConfigurations": [
                {
                    "name": str(ip_name),
                    "properties": {
                        "subnet": {
                            "id": "/subscriptions/{}/resourceGroups/{}/providers/microsoft.network/virtualNetworks/{}/subnets/{}"
                                .format(subscription_id, 
                                        resource_group_name, 
                                        management_network_name, 
                                        management_subnet_name)
                        },
                        "privateIPAllocationMethod": str(private_ip_allocation_method),
                    }
                }
            ]
        }
    }

    ctx.logger.info('Beginning nic creation')
    cntn = connection.AzureConnectionClient()

    response = cntn.azure_put(ctx, 
                   ("subscriptions/{}/resourcegroups/{}/" +
                    "providers/microsoft.network" +
                    "/networkInterfaces/{}" +
                    "?api-version={}").format(
                                            subscription_id, 
                                            resource_group_name, 
                                            network_interface_name, 
                                            api_version
                                            ),
                    json=json
                    )
    return response.status_code

def delete(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    network_interface_name = ctx.node.properties['network_interface_name']

    response = connection.AzureConnectionClient().azure_delete(
      ctx, 
      ("subscriptions/{}/resourceGroups/{}/providers/microsoft.network" + 
      "/networkInterfaces/{}?api-version={}").format(subscription_id, 
                                                    resource_group_name, 
                                                    network_interface_name, 
                                                    api_version
                                                    )
      )
    return response.status_code