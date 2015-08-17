from cloudify.exceptions import NonRecoverableError
import connection

def _get_vm_public_ip(ctx, azure_connection, subscription_id, resource_group, vm_name=None, nic=None):
	''' Get the public IP from a machine or a network interface. 

	'''

	if nic is not None:
		response = azure_connection.azure_get(
                                    ctx,
                                    ("subscriptions/{}" + 
                                    "/resourceGroups/{}/providers/" + 
                                    "microsoft.network/networkInterfaces/{}"
                                    "?api-version=2015-06-15"
                                    ).format(subscription_id, 
                                             resource_group, 
                                             nic
                                             )
                                    )

	elif vm_name is not None:
		response = azure_connection.azure_get(
                            ctx,
						    ("subscriptions/{}" +
						    "/resourceGroups/{}/providers" + 
						    "/Microsoft.Compute/virtualMachines/{}?" + 
						    "api-version=2015-06-15").format(subscription_id,
                                                             resource_group, 
                                                             vm_name
                                                            )
                            )
		nic_id = (response.json())(['properties']['networkProfile']
                                   ['networkInterfaces'][0]['id']
                                  )

		response = azure_connection.azure_get(
                            ctx, 
                            ("{}?api-version=2015-06-15").format(nic)
                            )
	else:
		raise NonRecoverableError('Unable to get public ip: missing argument')

	pip = (response.json())(['properties']['ipConfigurations'][0]['properties']
                            ['publicIPAddress']['id']
                           )

	response = requests.get(("https://management.azure.com/{}" + 
								"?api-version=2015-06-15").format(pip), headers=header)

	return (response.json())['properties']['ipAddress']