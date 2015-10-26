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
from cloudify.exceptions import NonRecoverableError

TIME_DELAY = 5


@operation
def create(**_):
    """Create an instance.

    :param ctx: The Cloudify ctx context.
    """
    utils.validate_node_property(constants.COMPUTE_KEY, ctx.node.properties)
    utils.validate_node_property(constants.FLAVOR_KEY, ctx.node.properties)
    utils.validate_node_property(constants.COMPUTE_USER_KEY, 
                                 ctx.node.properties)
    utils.validate_node_property(constants.COMPUTE_PASSWORD_KEY, 
                                 ctx.node.properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    location = azure_config[constants.LOCATION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]
    vm_size = ctx.node.properties[constants.FLAVOR_KEY]

    ctx.instance.runtime_properties[constants.COMPUTE_KEY] = vm_name

    # check availability name
    if not is_available(ctx=ctx):
        ctx.logger.info('VM creation not possible, {} already exist'
                                    .format(vm_name)
                        )
        raise utils.WindowsAzureError(400, '{} already exist'.format(vm_name))

    try:
        storage_account = utils.get_target_property(ctx,
            constants.INSTANCE_CONNECTED_TO_STORAGE_ACCOUNT,
            constants.STORAGE_ACCOUNT_KEY
        )
        ctx.logger.debug("get storage account {} from relationship"
                         .format(storage_account))
    except:
        storage_account = azure_config[constants.STORAGE_ACCOUNT_KEY]
        ctx.logger.debug("get storage account {} from azure_config"
                         .format(storage_account))
    
    ctx.instance.runtime_properties[constants.STORAGE_ACCOUNT_KEY]  = \
                                      storage_account
    storage_profile = _create_storage_profile(
                            vm_name, 
                                            storage_account,
                            ctx.node.properties[constants.IMAGE_KEY]
                            )
    os_profile = _create_os_profile(
                                            vm_name,
                        ctx.node.properties[constants.COMPUTE_USER_KEY], 
                        ctx.node.properties[constants.COMPUTE_PASSWORD_KEY],
                        ctx.node.properties
                                            )

    nics = nic.get_ids(ctx)
    networkInterfaces_list = []
    for _nic in nics:
        networkInterfaces_list.append({
            'properties': {
                'primary': _nic['primary']
            },
            'id': str(_nic['id'])
        })
    ctx.logger.debug('networkInterfaces_list: {}'.format(networkInterfaces_list))

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
            'osProfile': os_profile,
            'storageProfile': storage_profile,
            'networkProfile': {
                'networkInterfaces': networkInterfaces_list
            }
        }
    }

    try:
        ctx.logger.debug("Search for an availability_set")
        availability_set_id = utils.get_target_property(ctx,
            constants.INSTANCE_CONTAINED_IN_AVAILABILITY_SET,
            constants.AVAILABILITY_ID_KEY
        )
        ctx.logger.debug("availability_set found: {}"
                         .format(availability_set_id))
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
        utils.wait_status(ctx, 'instance', 'waiting for exception')
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


def _create_os_profile(vm_name, admin_username, admin_password, properties):
    """Create a dictionary to represent the os profile.
    The function determines if the requested machine is Windows or Unix
    based on the supplied properties in the context

    :param vm_name: The name of the VM to start.
    :param admin_username: The default username for the machine.
    :param admin_password: The default password for the machine.
    :param properties: The properties of the instance. It is used 
    to determine if the instance is a linux or a windows machine
    :return: The OS profile structure for the JSON of the machine.
    :rtype: dictionary.
    """

    os_profile =  {'computerName': str(vm_name),
                  'adminUsername': str(admin_username),
                  'adminPassword': str(admin_password)
                  }

    if constants.WINDOWS_AUTOMATIC_UPDATES_KEY in properties:
        # The machine is a Windows machine
        windows_update = properties[
                            constants.WINDOWS_AUTOMATIC_UPDATES_KEY]
        os_profile['windowsConfiguration'] = {
                        'provisionVMAgent': 'true',
                        'enableAutomaticUpdates': windows_update,
                        'winRM': {
                            'listeners': [{'protocol': 'http'}]
                            }
                        }
    elif constants.PUBLIC_KEY_KEY in properties:
        # The machine is a linux machine, the public key is required
        public_key = properties[constants.PUBLIC_KEY_KEY]
        os_profile['linuxConfiguration'] = {
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
    else:
        raise NonRecoverableError("Cannot determine if the VM" +
                                    " is a linux or windows instance.")

    return os_profile


def _create_storage_profile(vm_name, storage_account, image):
    """Create a storage profile to put in the JSON request to create a VM.

    :param vm_name: The name of the VM to start.
    :param storage_account: The name of the storage account for the OS disk.
    :param image: A dictionnary
    :return: The storage profile structure for the JSON of the machine.
    :rtype: dictionary.
    """
    storage_profile = {}
    create_option = 'FromImage'
    caching = "ReadWrite"
    os_disk_name = "{}_{}".format(vm_name,
                                  storage_account
                                 )
    os_disk_vhd = "https://{}.blob.core.windows.net/{}-vhds/{}.vhd".format(
                                            storage_account,
                                            vm_name,
                                            os_disk_name
                                            )

    if constants.OS_URI_KEY in image:
        ctx.logger.info("An uri as been given: trying to create VM from this.")
        uri_image = image[constants.OS_URI_KEY]
        os_type = image[constants.OS_TYPE_KEY]
        storage_profile = {
                            "osDisk": {
                                "osType": str(os_type),
                                "name": str(os_disk_name),
                                "createOption": str(create_option),
                                "image": {
                                    "uri": str(uri_image)
                                },
                                "vhd": {
                                    "uri": str(os_disk_vhd)
                                },
                                "caching": str(caching)
                           },
                        }
    elif constants.PUBLISHER_KEY in image:
        ctx.logger.info("Creating VM from marketplace.")
        publisher = image[constants.PUBLISHER_KEY]
        offer = image[constants.OFFER_KEY]
        sku = image[constants.SKU_KEY]
        distro_version = image[constants.SKU_VERSION_KEY]

        storage_profile = {
                    'imageReference': {
                        'publisher': str(publisher),
                        constants.OFFER_KEY: str(offer),
                        constants.SKU_KEY: str(sku),
                        constants.SKU_VERSION_KEY: str(distro_version)
                    },
                    'osDisk': {
                        'name': str(os_disk_name),
                        'createOption': str(create_option),
                        'vhd': {
                            'uri': str(os_disk_vhd)
                        },
                        "caching": str(caching)
                    }
                }
    else:
        raise NonRecoverableError("Image structure is missing arguments.")


    return storage_profile
