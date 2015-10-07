# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )
from public_ip import get_id as get_public_ip_id
from subnet import get_id as get_subnet_id

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

def _get_vm_ip(ctx, public=False):
    """Get the ip of a network interface card id (relationship function for an instance).

    :param ctx: The Cloudify ctx context.
    :return: The ip of a network interface card.
    :rtype: string
    """
    utils.validate_node_property(constants.COMPUTE_KEY, ctx.node.properties)

    azure_connection = connection.AzureConnectionClient()

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]
    nic = utils.get_target_property(
        ctx,
        constants.INSTANCE_CONNECTED_TO_NIC,
        constants.NETWORK_INTERFACE_KEY
    )

    if nic is not None:
        response = azure_connection.azure_get(
                                    ctx,
                                    ("subscriptions/{}" + 
                                    "/resourceGroups/{}/providers/" + 
                                    "microsoft.network/networkInterfaces/{}"
                                    "?api-version={}"
                                    ).format(subscription_id, 
                                             resource_group_name, 
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
                                                     resource_group_name, 
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

    if public:
        pip = (response.json())['properties']['ipConfigurations'][0]['properties']['publicIPAddress']['id']
    else:
        return (response.json())['properties']['ipConfigurations'][0]['properties']['privateIPAddress']

    response = azure_connection.azure_get(
                                        ctx,
                                        "{}?api-version={}"
                                                        .format(pip,
                                                                api_version
                                                                )
                                        )

    return (response.json())['properties']['ipAddress']


def get_provisioning_state(**_):
    """Get the provisioning state of a network interface card.

    :param ctx: The Cloudify ctx context.
    :return: The provisioning state of a network interface card.
    :rtype: string
    """
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = ctx.node.properties[constants.NETWORK_INTERFACE_KEY]


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


@operation
def create(**_):
    """Create a network interface card.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.node.properties)
    
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = ctx.node.properties[constants.NETWORK_INTERFACE_KEY]
    private_ip_allocation_method = "Dynamic"
    subnet_id = get_subnet_id(ctx=ctx)

    # Place the network name in runtime_properties for relationships
    ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY] = \
        network_interface_name
    ctx.instance.runtime_properties['subnet_id'] = subnet_id

    json ={
        "location": str(location),
        "properties": {
            "ipConfigurations": [
                {
                    "name": str(network_interface_name),
                    "properties": {
                        "subnet": {
                            "id": str(subnet_id)
                        },
                        "privateIPAllocationMethod": str(private_ip_allocation_method)
                    }
                }
            ]
        }
    }

    ctx.logger.info('create NIC : ' + network_interface_name)
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

@operation
def add_public_ip(**_):
    """Add a public ip to a network interface card.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    location = azure_config[constants.LOCATION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = ctx.source.node.properties[constants.NETWORK_INTERFACE_KEY]
    private_ip_allocation_method = "Dynamic"
    subnet_id = ctx.source.instance.runtime_properties['subnet_id']
    public_ip_id = get_public_ip_id(ctx=ctx)

    json ={
        "location": str(location),
        "properties": {
            "ipConfigurations": [
                {
                    "name": str(network_interface_name),
                    "properties": {
                        "subnet": {
                            "id": str(subnet_id)
                        },
                        "privateIPAllocationMethod": str(private_ip_allocation_method),
                        "publicIPAddress":{  
                            "id": str(public_ip_id)
                        },
                    }
                }
            ]
        }
    }

    ctx.logger.info('Update NIC : ' + network_interface_name + " (ADD public_ip)")
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

#TODO not implemented yet
#@operation
#def remove_public_ip(**_):
    
@operation
def delete(**_):
    """Delete a network interface card.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.node.properties)
    utils.validate_node_property(constants.DELETABLE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = ctx.node.properties[constants.NETWORK_INTERFACE_KEY]
    deletable = ctx.node.properties[constants.DELETABLE_KEY]
    
    if deletable:
        ctx.logger.info('Propertie deletable set to True.')
        ctx.logger.info('Deleting NIC {}.'.format(network_interface_name))

        cntn = connection.AzureConnectionClient()
        response = cntn.azure_delete(
        ctx, 
        ("subscriptions/{}/resourceGroups/{}/providers/microsoft.network" + 
        "/networkInterfaces/{}?api-version={}").format(subscription_id, 
                                                    resource_group_name, 
                                                    network_interface_name, 
                                                    api_version
                                                    )
        )
        return response.status_code

    else:
        ctx.logger.info('Propertie deletable set to False.')
        ctx.logger.info('Not deleting NIC {}.'.format(network_interface_name))
        return 0


def get_id(ctx):
    """Get the id of a network interface card (relationship function for an instance).

    :param ctx: The Cloudify ctx context.
    :return: The id of a network interface card.
    :rtype: string
    """
    azure_config = utils.get_azure_config(ctx)
    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]

    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = utils.get_target_property(
        ctx,
        constants.INSTANCE_CONNECTED_TO_NIC,
        constants.NETWORK_INTERFACE_KEY
    )

    response = connection.AzureConnectionClient().azure_get(
        ctx,
        ('subscriptions/{}' +
         '/resourceGroups/{}' +
         '/providers/microsoft.network' +
         '/networkInterfaces/{}' +
         '?api-version={}').format(
            subscription_id,
            resource_group_name,
            network_interface_name,
            api_version
        )
    )
    return response.json()['id']