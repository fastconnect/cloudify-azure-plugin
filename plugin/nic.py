from cloudify.exceptions import NonRecoverableError
import connection
import constants

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
                            "{}?api-version={}".format(pip, api_version)
                            )

    return (response.json())['properties']['ipAddress']