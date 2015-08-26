# -*- coding: utf-8 -*-
import random
import time
import re
#Local import
from plugin import utils
from plugin import constants
from plugin import connection
from plugin import nic

#Cloudify imports
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation


@operation
def create(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('compute_name', ctx.node.properties)
    utils.validate_node_property('location', ctx.node.properties)
    utils.validate_node_property('flavor_id', ctx.node.properties)
    utils.validate_node_property('publisherName', ctx.node.properties)
    utils.validate_node_property('offer', ctx.node.properties)
    utils.validate_node_property('sku', ctx.node.properties)
    utils.validate_node_property('version', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.node.properties)
    utils.validate_node_property('storage_account', ctx.node.properties)
    utils.validate_node_property('compute_user', ctx.node.properties)
    utils.validate_node_property('compute_password', ctx.node.properties)
    utils.validate_node_property('public_key', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties['compute_name']
    resource_group_name = ctx.node.properties['resource_group_name']
    vm_type = "Microsoft.Compute/virtualMachines"
    location = ctx.node.properties['location']
    vm_size = ctx.node.properties['flavor_id']
    publisher = ctx.node.properties['publisherName']
    offer = ctx.node.properties['offer']
    sku = ctx.node.properties['sku']
    distro_version = ctx.node.properties['version']
    network_interface_name = ctx.node.properties['network_interface_name']
    storage_account = ctx.node.properties['storage_account']
    create_option = 'FromImage'
    os_disk_name = "{}_{}_{}.vhd".format(vm_name, 
                                       storage_account,
                                       random.randint(0,1000)
                                       )
    os_disk_vhd = "https://{}.blob.core.windows.net/vhds/{}.vhd".format(
                                                    storage_account,
                                                    os_disk_name
                                                    )
    computer_name = ctx.node.properties['compute_name']
    network_interface = ctx.node.properties['network_interface_name']
    admin_username = ctx.node.properties['compute_user']
    admin_password = ctx.node.properties['compute_password']
    public_key = ctx.get_resource(ctx.node.properties['public_key'])

    json = {
	    'id':('/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute' +
             '/virtualMachines/{}').format(subscription_id,
                                         resource_group_name,
                                         vm_name
                                         ),
	    'name':str(vm_name),
	    'type':'Microsoft.Compute/virtualMachines',
	    'location': str(location),
	    'properties':{
	        'hardwareProfile':{
	            'vmSize': str(vm_size)
	         },
	        'osProfile':{
	            'computerName': str(computer_name),
	            'adminUsername': str(admin_username),
	            'adminPassword': str(admin_password),
	            'linuxConfiguration':{
                    'disablePasswordAuthentication': 'true',
                    'ssh': {
                        'publicKeys': [ { 
                            'path': '/home/{}/.ssh/authorized_keys'.format(
                                                            admin_username
                                                            ),
                            'keyData': str(public_key)
                        } ]
                    }
                }
	        },
	        'storageProfile':{
	            'imageReference':{
	                'publisher': str(publisher),
	                'offer': str(offer),
	                'sku': str(sku),
	                'version': str(distro_version)
	            },
	            'osDisk':{
	                'vhd':{
	                    'uri': str(os_disk_vhd)
	                },
	                "caching":"ReadWrite",
	                'name': str(os_disk_name),
	                'createOption': str(create_option)
	            }
	        },
	        'networkProfile':{
	            'networkInterfaces':
	            [
	            {
	                'id':('/subscriptions/{}/resourcegroups/{}' + 
                        '/providers/Microsoft.Network/networkInterfaces/{}').
                        format(
                            subscription_id,
                            resource_group_name, 
                            network_interface
                            )
	            }
	            ]
	        }
	    }
	}

    ctx.logger.info('Beginning vm creation: {}'.format(ctx.instance.id))
    cntn = connection.AzureConnectionClient()
    cntn.azure_put(ctx, 
                   ("subscriptions/{}/resourcegroups/{}/" +
                    "providers/Microsoft.Compute" +
                    "/virtualMachines/{}" +
                    "?validating=true&api-version={}").format(
                                                    subscription_id, 
                                                    resource_group_name, 
                                                    vm_name, 
                                                    api_version
                                                    ),
                    json=json
                    )

    status = get_vm_provisioning_state()

    while status == constants.CREATING:
        ctx.logger.info('{} is still {}'.format(vm_name, status))
        time.sleep(20)
        status = get_vm_provisioning_state()

    if status != constants.SUCCEEDED:
        raise NonRecoverableError('Provisionning: {}.'.format(status))
    else:
        ctx.logger.info('{} {}'.format(vm_name, status))
        if re.search(r'manager', ctx.instance.id):
            # Get public ip of the manager
            ip = nic._get_vm_ip(ctx, public=True)
        else:
            # Get private ip of the agent
            ip = nic._get_vm_ip(ctx)

        ctx.logger.info(
                'Machine is running at {}.'.format(ip)
                )
        ctx.instance.runtime_properties['ip'] = ip   


@operation
def delete(**_):
    utils.validate_node_property('subscription_id',ctx.node.properties)
    utils.validate_node_property('compute_name',ctx.node.properties)
    utils.validate_node_property('resource_group_name',ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties['compute_name']
    resource_group_name = ctx.node.properties['resource_group_name']

    ctx.logger.info('Deleting vm {}.'.format(vm_name))
    response = connection.AzureConnectionClient().azure_delete(
        ctx, 
        ("subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute" + 
        "/virtualMachines/{}?api-version={}").format(subscription_id, 
                                                     resource_group_name, 
                                                     vm_name, api_version
                                                     )
        )
    return response.status_code


def get_vm_provisioning_state(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('compute_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties['compute_name']
    resource_group_name = ctx.node.properties['resource_group_name']

    response = connection.AzureConnectionClient().azure_get(
            ctx, 
            ("subscriptions/{}/resourcegroups/{}/"+
            "providers/Microsoft.Compute/virtualMachines"+
            "/{}?InstanceView&api-version={}").format(
                subscription_id, 
                resource_group_name, 
                vm_name,
                api_version
            )
        )
    jsonGet = response.json()
    status_vm = jsonGet['properties']['provisioningState']
    return status_vm

def get_nic_virtual_machine_id(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    network_interface_name = ctx.node.properties['network_interface_name']
    try:
        response = connection.AzureConnectionClient().azure_get(
                ctx, 
                ("subscriptions/{}/resourcegroups/{}/"+
                "providers/microsoft.network/networkInterfaces/{}"+
                "/?api-version={}").format(
                    subscription_id, 
                    resource_group_name,
                    network_interface_name, 
                    api_version
                )
            )
        jsonGet = response.json()
        ctx.logger.debug(jsonGet)

        vm_id = jsonGet['properties']['virtualMachine']['id']
    except KeyError :
        return None
     
    return vm_id
