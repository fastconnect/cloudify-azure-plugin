# -*- coding: utf-8 -*-
import random
#Local import
from plugin import utils
from plugin import constants
from plugin import connection

#Cloudify imports
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

def check_vm_status(**_):
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
                vm_name, api_version
            )
        )
    jsonGet = response.json()
    status_vm = jsonGet['properties']['provisioningState']
    return status_vm

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
    utils.validate_node_property('create_option', ctx.node.properties)
    utils.validate_node_property('compute_user', ctx.node.properties)
    utils.validate_node_property('compute_password', ctx.node.properties)

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
    create_option = ctx.node.properties['create_option']
    os_disk_name = "{}_{}_{}.vhd".format(vm_name, 
                                       storage_account,
                                       random.randint(0,1000)
                                       )
    os_disk_vhd = "https://{0}.blob.core.windows.net/vhds/{0}.vhd".format(
                                                    storage_account,
                                                    os_disk_name
                                                    )
    computer_name = ctx.node.properties['compute_name']
    network_interface = ctx.node.properties['network_interface_name']
    admin_username = ctx.node.properties['compute_user']
    admin_password = ctx.node.properties['compute_password']

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
                    'disablePasswordAuthentication': 'false'
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

    connection.AzureConnectionClient().azure_put(
        ctx,
        ("subscriptions/{}/resourcegroups/{}/providers/Microsoft.Compute" +
        "/virtualMachines/{}?validating=true&api-version={}").format(
                    subscription_id, 
                    resource_group_name, 
                    vm_name, 
                    api_version
                    ),
        json=json
        )


@operation
def delete(**_):
    utils.validate_node_property('subscription_id',ctx.node.properties)
    utils.validate_node_property('compute_name',ctx.node.properties)
    utils.validate_node_property('resource_group_name',ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION
    vm_name = ctx.node.properties['compute_name']
    resource_group_name = ctx.node.properties['resource_group_name']

    connection.AzureConnectionClient().azure_delete(
        ctx, 
        ("subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute" + 
        "/virtualMachines/{}?api-version={}").format(
            subscription_id, 
            resource_group_name, 
            vm_name, api_version
            )
        )
