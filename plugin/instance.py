# -*- coding: utf-8 -*-
from plugin import utils
from plugin import constants
from plugin import connection
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

@operation
def creation_validation(**_):
    """ This checks that all user supplied info is valid """

    for property_key in constants.INSTANCE_REQUIRED_PROPERTIES:
        utils.validate_node_property(property_key, ctx.node.properties)

@operation
def run_instances(**_):
    
    azure_client = connection.AzureConnectionClient().client()

    linux_config = LinuxConfigurationSet(
        ctx.node.properties['name'], 
        'administrateur',
        'Azerty@01', 
        disable_ssh_password_authentication = False
    )

    os_hd = OSVirtualHardDisk(ctx.node.properties['image_id'], 
                              ctx.node.properties['storage_account_URL'])

    azure_client.create_deployment(
        service_name=ctx.node.properties['cloud_service'],
        deployment_name=ctx.node.properties['name'],
        deployment_slot='production',
        label=ctx.node.properties['name'],
        role_name=ctx.node.properties['name'],
        system_config=linux_config,
        os_virtual_hard_disk=os_hd,
        role_size='Small'
        )

    status = azure_client.get_deployment_by_name(
                            ctx.node.properties['cloud_service'],
                            ctx.node.properties['name']
                            ).status

    ctx.logger.info('{0} instance is {1}'
                    .format(
                        ctx.node.properties['name'],
                        status
                    )
    )
    return status