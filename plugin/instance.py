# -*- coding: utf-8 -*-
import random
import re
#Local import
from plugin import (utils,
                    constants,
                    connection,
                    nic,
                    public_ip
                    )

#Cloudify imports
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

TIME_DELAY = 5

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
    storage_account = ctx.node.properties['storage_account']
    create_option = 'FromImage'

    #check availability name
    if not is_available(ctx=ctx):
        ctx.logger.info('VM creation not possible, {} already exist'.format(vm_name))
        raise utils.WindowsAzureError(400,'{} already exist'.format(vm_name))

    number = random.randint(0,1000)
    os_disk_name = "{}_{}_{}.vhd".format(vm_name,
                                       storage_account,
                                       number
                                       )
    os_disk_vhd = "https://{}.blob.core.windows.net/vhds/{}.vhd".format(
                                                    storage_account,
                                                    os_disk_name
                                                    )

    #generation of nic and public ip name
    network_interface_name = "{}_nic_{}".format(vm_name,
                                                number
                                                )
    ctx.instance.runtime_properties['network_interface_name'] = \
                                       network_interface_name
    public_ip_name = "{}_pip_{}".format(vm_name, number)
    ctx.instance.runtime_properties['public_ip_name'] = public_ip_name

    #generation of public_ip
    public_ip.create(ctx=ctx)
    utils.wait_status(ctx, 'public_ip')

    #generation of nic
    nic.create(ctx=ctx)
    utils.wait_status(ctx, 'nic')

    computer_name = ctx.node.properties['compute_name']
    admin_username = ctx.node.properties['compute_user']
    admin_password = ctx.node.properties['compute_password']
    public_key = ctx.node.properties['public_key']

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
                            network_interface_name
                            )
	            }
	            ]
	        }
	    }
	}
    ctx.logger.debug('JSON: {}'.format(json))
    ctx.logger.info('Beginning vm creation: {}'.format(ctx.instance.id))
    try:
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

        utils.wait_status(ctx, 'instance')

        ctx.logger.info('VM� has been started.')
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
    except utils.WindowsAzureError as e:
        ctx.logger.info('Creation vm failed: {}'.format(ctx.instance.id))
        ctx.logger.info('Error code: {}'.format(e.code))
        ctx.logger.info('Error message: {}'.format(e.message))
        #deleting nic
        nic.delete(ctx=ctx)
        try:
            utils.wait_status(ctx, 'nic',start_status=constants.DELETING)
        except utils.WindowsAzureError:
            pass

        #deletin puplic ip
        public_ip.delete(ctx=ctx)
        try:
            utils.wait_status(ctx, 'public_ip',start_status=constants.DELETING)
        except utils.WindowsAzureError:
            pass

        raise utils.WindowsAzureError(e.code, e.message)


@operation
def delete(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('compute_name', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('network_interface_name', ctx.instance.runtime_properties)
    utils.validate_node_property('public_ip_name', ctx.instance.runtime_properties)

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

    #wait vm deletion
    try:
        utils.wait_status(ctx, 'instance',start_status=constants.DELETING)
    except utils.WindowsAzureError:
        pass

    #deleting nic
    nic.delete(ctx=ctx)
    try:
        utils.wait_status(ctx, 'nic',start_status=constants.DELETING)
    except utils.WindowsAzureError:
        pass

    #deletin puplic ip
    public_ip.delete(ctx=ctx)
    try:
        utils.wait_status(ctx, 'public_ip',start_status=constants.DELETING)
    except utils.WindowsAzureError:
        pass

    return response.status_code


@operation
def start(**_):
    ctx.logger.info("VM starts.")
    

@operation
def stop(**_):
    ctx.logger.info("VM stops.")


def get_provisioning_state(**_):
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
    utils.validate_node_property('network_interface_name', ctx.instance.runtime_properties)

    subscription_id = ctx.node.properties['subscription_id']
    api_version = constants.AZURE_API_VERSION_06
    resource_group_name = ctx.node.properties['resource_group_name']
    network_interface_name = ctx.instance.runtime_properties['network_interface_name']
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

def is_available(**_):
    utils.validate_node_property('subscription_id', ctx.node.properties)
    utils.validate_node_property('resource_group_name', ctx.node.properties)
    utils.validate_node_property('compute_name', ctx.node.properties)

    subscription_id = ctx.node.properties['subscription_id']
    resource_group_name = ctx.node.properties['resource_group_name']
    vm_name = ctx.node.properties['compute_name']
    api_version = constants.AZURE_API_VERSION_06

    response = connection.AzureConnectionClient().azure_get(
        ctx,
        ("subscriptions/{}/resourcegroups/{}/"+
            "providers/Microsoft.Compute/virtualmachines"+
            "?api-version={}").format(
                subscription_id,
                resource_group_name,
                api_version
        )
    )
    jsonGet = response.json()
    ctx.logger.debug(jsonGet)

    list = jsonGet['value']
    for vm in list:
        if vm['name']== vm_name:
            return False

    return True
