# -*- coding: utf-8 -*-
import random
import time
import re
#Local import
try:
    from plugin import utils
    from plugin import constants
    from plugin import connection
    from plugin import nic
    from plugin import public_ip
except:
    import utils
    import constants
    import connection
    import nic
    import public_ip

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
    #utils.validate_node_property('network_interface_name', ctx.node.properties)
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
    #network_interface_name = ctx.node.properties['network_interface_name']
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
    status_ip = constants.CREATING
    while status_ip != constants.SUCCEEDED :
        status_ip = public_ip.get_public_ip_provisioning_state(ctx=ctx)
        time.sleep(TIME_DELAY)
    if constants.SUCCEEDED != status_ip :
        ctx.logger.info('status creation public ip is : ' + str(status_ip))
        raise NonRecoverableError('Failed provisionning Public IP : {}.'.format(status_ip))

    #generation of nic
    nic.create(ctx=ctx)
    status_nic = constants.CREATING
    while status_nic == constants.CREATING :
        status_nic = nic.get_provisioning_state(ctx=ctx)
        time.sleep(TIME_DELAY)
    if constants.SUCCEEDED != status_nic :
        raise NonRecoverableError('Failed provisionning nic : {}.'.format(status_nic))

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
    except utils.WindowsAzureError as e:
        ctx.logger.info('Creation vm failed: {}'.format(ctx.instance.id))
        #deletin puplic ip
        public_ip.delete(ctx=ctx)

        status_ip = constants.DELETING
        try:
            while status_ip == constants.DELETING :
                status_ip = public_ip.get_public_ip_provisioning_state(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        #deleting nic
        nic.delete(ctx=ctx)
        try:
            nic.get_provisioning_state(ctx=ctx)
        except utils.WindowsAzureError:
            pass
        raise utils.WindowsAzureError(e.code, e.message)


@operation
def delete(**_):
    utils.validate_node_property('subscription_id',ctx.node.properties)
    utils.validate_node_property('compute_name',ctx.node.properties)
    utils.validate_node_property('resource_group_name',ctx.node.properties)
    utils.validate_node_property('network_interface_name',ctx.node.properties)
    utils.validate_node_property('public_ip_name',ctx.node.properties)

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

    #deletin puplic ip
    public_ip.delete(ctx=ctx)

    status_ip = constants.DELETING
    try:
        while status_ip == constants.DELETING :
            status_ip = public_ip.get_public_ip_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
    except utils.WindowsAzureError:
        pass

    #wait vm deletion
    try:
        status = get_vm_provisioning_state()
        while status == constants.DELETING:
            ctx.logger.info('{} is still {}'.format(vm_name, status))
            time.sleep(20)
            status = get_vm_provisioning_state()
    except utils.WindowsAzureError:
        pass

    #deleting nic
    nic.delete(ctx=ctx)
    try:
        nic.get_provisioning_state(ctx=ctx)
    except utils.WindowsAzureError:
        pass

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
    #utils.validate_node_property('network_interface_name', ctx.node.properties)

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
