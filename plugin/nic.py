# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    connection,
                    )
from public_ip import get_public_address_id

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

def _get_vm_ip(ctx, public=False):
    ''' 
        Get the public IP from a machine or a network interface. 
    '''
    utils.validate_node_property(constants.COMPUTE_KEY, ctx.node.properties)
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.instance.runtime_properties)

    azure_connection = connection.AzureConnectionClient()

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]
    nic = ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY]

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
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY]


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
    utils.validate_node_property(constants.VIRTUAL_NETWORK_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SUBNET_KEY, ctx.node.properties)
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.instance.runtime_properties)
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_06
    virtual_network_name = ctx.node.properties[constants.VIRTUAL_NETWORK_KEY]
    subnet_name = ctx.node.properties[constants.SUBNET_KEY]
    network_interface_name = ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY]
    public_ip_name = ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY]
    private_ip_allocation_method = "Dynamic"
    public_ip_id = get_public_address_id(ctx)

    json ={
        "location": str(location),
        "properties": {
            "ipConfigurations": [
                {
                    "name": str(public_ip_name),
                    "properties": {
                        "subnet": {
                            "id": "/subscriptions/{}/resourceGroups/{}/providers/microsoft.network/virtualNetworks/{}/subnets/{}"
                                .format(subscription_id, 
                                        resource_group_name, 
                                        virtual_network_name,
                                        subnet_name)
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

def delete(**_):
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY]

    ctx.logger.info('delete NIC : ' + network_interface_name)
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