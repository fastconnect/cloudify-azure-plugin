# -*- coding: utf-8 -*-
#Local import
from plugin import utils
from plugin import constants
from plugin import connection
#Azure imports
from azure.servicemanagement import (ServiceManagementService,
                                     LinuxConfigurationSet,
                                     OSVirtualHardDisk,
                                     )
from azure.storage import BlobService
from azure import (WindowsAzureConflictError,
                   WindowsAzureError
                   )
#Cloudify imports
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation


@operation
def creation_validation(**_):
    """ This checks that all user supplied info is valid """

    for property_key in constants.INSTANCE_REQUIRED_PROPERTIES:
        utils.validate_node_property(property_key, ctx.node.properties)


@operation
def start(**_):

    azure_client = connection.AzureConnectionClient().client()

    linux_config = LinuxConfigurationSet(ctx.node.properties['name'],
        'administrateur',
        'Azerty@01',
        disable_ssh_password_authentication=False)

    blob_service = connection.AzureConnectionClient().storageClient()

    blob_url = blob_service.make_blob_url(ctx.node.properties['storage_container'],
                    '{0}.vhd'.format(ctx.node.properties['name']),
                    ctx.node.properties['storage_account'])

    os_hd = OSVirtualHardDisk(ctx.node.properties['image_id'],
                              blob_url)

    ctx.logger.info('Trying to deploy {0} {1} {2}'
                    .format(ctx.node.properties['cloud_service'],
                        ctx.node.properties['name'],
                        blob_url))
    utils.azure_request(ctx,azure_client, 'create_virtual_machine_deployment',
                        service_name=ctx.node.properties['cloud_service'],
                        deployment_name=ctx.node.properties['name'], 
                        deployment_slot='production',
                        label=ctx.node.properties['name'],
                        role_name=ctx.node.properties['name'],
                        system_config=linux_config,
                        os_virtual_hard_disk=os_hd,
                        role_size='Small'
                        )
   
    status = azure_client.get_deployment_by_name(ctx.node.properties['cloud_service'],
                            ctx.node.properties['name']).status

    ctx.logger.info('{0} instance is {1}'
                    .format(ctx.node.properties['name'],
                        status))
    return status


@operation
def stop(**_):

    azure_client = connection.AzureConnectionClient().client()

    utils.azure_request(ctx, azure_client, 'delete_deployment',
                        ctx.node.properties['cloud_service'],
                        ctx.node.properties['name'], 
                        True
                        )

    return constants.REQUEST_SUCCEEDED