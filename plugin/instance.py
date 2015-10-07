# -*- coding: utf-8 -*-
import re
import inspect
# Local import
from plugin import (utils,
                    constants,
                    connection,
                    nic
                    )

# Cloudify imports
from cloudify import ctx
from cloudify.decorators import operation

TIME_DELAY = 5


@operation
def create(**_):
    """Create an instance.

    :param ctx: The Cloudify ctx context.
    """
    utils.validate_node_property(constants.COMPUTE_KEY, ctx.node.properties)
    utils.validate_node_property(constants.FLAVOR_KEY, ctx.node.properties)
    utils.validate_node_property(constants.PUBLISHER_KEY, ctx.node.properties)
    utils.validate_node_property(constants.OFFER_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SKU_KEY, ctx.node.properties)
    utils.validate_node_property(constants.SKU_VERSION_KEY,
                                 ctx.node.properties)
    utils.validate_node_property(constants.COMPUTE_USER_KEY, 
                                 ctx.node.properties)
    utils.validate_node_property(constants.COMPUTE_PASSWORD_KEY, 
                                 ctx.node.properties)
    utils.validate_node_property(constants.PUBLIC_KEY_KEY, 
                                 ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    location = azure_config[constants.LOCATION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    admin_username = ctx.node.properties[constants.COMPUTE_USER_KEY]
    admin_password = ctx.node.properties[constants.COMPUTE_PASSWORD_KEY]
    public_key = ctx.node.properties[constants.PUBLIC_KEY_KEY]
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]
    vm_size = ctx.node.properties[constants.FLAVOR_KEY]
    publisher = ctx.node.properties[constants.PUBLISHER_KEY]
    offer = ctx.node.properties[constants.OFFER_KEY]
    sku = ctx.node.properties[constants.SKU_KEY]
    distro_version = ctx.node.properties[constants.SKU_VERSION_KEY]
    create_option = 'FromImage'

    ctx.instance.runtime_properties[constants.COMPUTE_KEY] = vm_name

    try:
        storage_account = utils.get_target_property(ctx,
            constants.INSTANCE_CONNECTED_TO_STORAGE_ACCOUNT,
            constants.STORAGE_ACCOUNT_KEY
        )
        ctx.logger.debug("get storage account {} from relationship".format(storage_account))
    except:
        storage_account = azure_config[constants.STORAGE_ACCOUNT_KEY]
        ctx.logger.debug("get storage account {} from azure_config".format(storage_account))
    
    
    ctx.instance.runtime_properties[constants.STORAGE_ACCOUNT_KEY]  = storage_account

    # check availability name
    if not is_available(ctx=ctx):
        ctx.logger.info('VM creation not possible, {} already exist'
                                    .format(vm_name)
                        )
        raise utils.WindowsAzureError(400, '{} already exist'.format(vm_name))

    os_disk_name = "{}_{}.vhd".format(vm_name,
                                      storage_account
                                     )
    os_disk_vhd = "https://{}.blob.core.windows.net/{}-vhds/{}.vhd".format(
                                            storage_account,
                                            vm_name,
                                            os_disk_name
                                            )

    nic_id = nic.get_id(ctx)

    json = {
        'id': ('/subscriptions/{}/resourceGroups/{}' +
               '/providers/Microsoft.Compute' +
               '/virtualMachines/{}').format(subscription_id,
                                             resource_group_name,
                                             vm_name
                                             ),
        'name': str(vm_name),
        'type': 'Microsoft.Compute/virtualMachines',
        constants.LOCATION_KEY: str(location),
        'properties': {
            'hardwareProfile': {
                'vmSize': str(vm_size)
            },
            'osProfile': {
                'computerName': str(vm_name),
                'adminUsername': str(admin_username),
                'adminPassword': str(admin_password),
                'linuxConfiguration': {
                    'disablePasswordAuthentication': 'true',
                    'ssh': {
                        'publicKeys': [{
                            'path': '/home/{}/.ssh/authorized_keys'.format(
                                admin_username
                            ),
                            'keyData': str(public_key)
                        }]
                    }
                }
            },
            'storageProfile': {
                'imageReference': {
                    'publisher': str(publisher),
                    constants.OFFER_KEY: str(offer),
                    constants.SKU_KEY: str(sku),
                    constants.SKU_VERSION_KEY: str(distro_version)
                },
                'osDisk': {
                    'vhd': {
                        'uri': str(os_disk_vhd)
                    },
                    "caching": "ReadWrite",
                    'name': str(os_disk_name),
                    'createOption': str(create_option)
                }
            },
            'networkProfile': {
                'networkInterfaces':[
                    {
                        'id': str(nic_id)
                    }
                ]
            }
        }
    }

    try:
        ctx.logger.debug("Search for an availability_set")
        availability_set_id = utils.get_target_property(ctx,
            constants.INSTANCE_CONTAINED_IN_AVAILABILITY_SET,
            constants.AVAILABILITY_ID_KEY
        )
        ctx.logger.debug("availability_set found: {}".format(availability_set_id))
        json['properties']['availabilitySet']={'id': str(availability_set_id)}
    except:
        ctx.logger.debug('Instance not contained in an availability set')
        pass

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

        ctx.logger.info('VM has been started.')
        if re.search(r'manager', ctx.instance.id):
            # Get manager's public ip
            ctx.instance.runtime_properties['public_ip'] = \
                nic._get_vm_ip(ctx, public=True)
            ctx.logger.info('Public IP manager: {}'
                             .format(
                                 ctx.instance.runtime_properties['public_ip']
                                 )
                             )

        
        # Get agent's private ip 
        ip = nic._get_vm_ip(ctx)

        ctx.logger.info(
            'Machine is running at {}.'.format(ip)
        )
        ctx.instance.runtime_properties['ip'] = ip
    except utils.WindowsAzureError as e:
        ctx.logger.info('Creation vm failed: {}'.format(ctx.instance.id))
        ctx.logger.info('Error code: {}'.format(e.code))
        ctx.logger.info('Error message: {}'.format(e.message))

        raise utils.WindowsAzureError(e.code, e.message)


@operation
def delete(**_):
    """Delete an instance.

    :param ctx: The Cloudify ctx context.
    :return: The status code of the REST request.
    :rtype: int
    """
    utils.validate_node_property(constants.COMPUTE_KEY, ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]

    ctx.logger.info('Deleting vm {}.'.format(vm_name))
    response = connection.AzureConnectionClient().azure_delete(
        ctx,
        ("subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute" +
         "/virtualMachines/{}?api-version={}").format(subscription_id,
                                                      resource_group_name,
                                                      vm_name, api_version
                                                      )
    )

    # wait vm deletion
    try:
        utils.wait_status(ctx, 'instance')
    except utils.WindowsAzureError:
        pass

    return response.status_code


@operation
def start(**_):
    """Start an instance.
    (Doing nothing)

    :param ctx: The Cloudify ctx context.
    """
    ctx.logger.info("VM starts.")


@operation
def stop(**_):
    """Stop an instance.
    (Doing nothing)

    :param ctx: The Cloudify ctx context.
    """
    ctx.logger.info("VM stops.")


def get_provisioning_state(**_):
    """Get the provisioning state of an instance.

    :param ctx: The Cloudify ctx context.
    :return: The provisioning state of an instance.
    :rtype: string
    """

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.instance.runtime_properties[constants.COMPUTE_KEY]

    response = connection.AzureConnectionClient().azure_get(
        ctx,
        ("subscriptions/{}/resourcegroups/{}/" +
         "providers/Microsoft.Compute/virtualMachines" +
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
    """DEPRECATED
    Get the id of the network interface card of an instance.

    :param ctx: The Cloudify ctx context.
    :return: The id of the network interface card.
    :rtype: string
    """
    utils.validate_node_property(constants.NETWORK_INTERFACE_KEY, 
                                 ctx.instance.runtime_properties)
    
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    network_interface_name = \
        ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY]

    try:
        response = connection.AzureConnectionClient().azure_get(
            ctx,
            ("subscriptions/{}/resourcegroups/{}/" +
             "providers/microsoft.network/networkInterfaces/{}" +
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
    except KeyError:
        return None

    return vm_id


def is_available(**_):
    """Check the availability of an instance name.

    :param ctx: The Cloudify ctx context.
    :return: A the availability.
    :rtype: bool
    """
    utils.validate_node_property(constants.COMPUTE_KEY, 
                                 ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]
    api_version = constants.AZURE_API_VERSION_06

    response = connection.AzureConnectionClient().azure_get(
        ctx,
        ("subscriptions/{}/resourceGroups/{}/" +
         "providers/Microsoft.Compute/virtualmachines" +
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
        if vm['name'] == vm_name:
            return False

    return True

def get_json_from_azure(**_):
    """Get the json of an instance.

    :param ctx: The Cloudify ctx context.
    :return: The json of an instance.
    :rtype: dictionary
    """

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    vm_name = ctx.instance.runtime_properties[constants.COMPUTE_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview

    response = connection.AzureConnectionClient().azure_get(
                    ctx,
                    ('subscriptions/{}' + 
                    '/resourceGroups/{}' +
                    '/providers/Microsoft.Compute/virtualMachines/{}' +
                    '?api-version={}').format(subscription_id,
                                              resource_group_name,
                                              vm_name,
                                              api_version
                                              )
                    )

    return response.json()