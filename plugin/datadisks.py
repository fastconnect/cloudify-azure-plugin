from plugin import (utils,
                    constants,
                    instance,
                    connection
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

@operation
def create(**_):
    utils.validate_node_property(constants.DISKS_KEY, ctx.node.properties)    
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    vm_name = utils.get_target_property(
                                        ctx, 
                                        constants.DISK_ATTACH_TO_INSTANCE,
                                        constants.COMPUTE_KEY
                                        )

    disks = ctx.node.properties[constants.DISKS_KEY]
    api_version = constants.AZURE_API_VERSION_06
    
    try:
        storage_account = utils.get_target_property(
                                        ctx, 
                                        constants.DISK_CONTAINED_IN_STORAGE_ACCOUNT,
                                        constants.STORAGE_ACCOUNT_KEY
                                        )
        ctx.logger.info("Use storage account {} in DISK_CONTAINED_IN_STORAGE_ACCOUNT relationship".format(storage_account))
    except NonRecoverableError:
        storage_account = utils.get_target_property(
                                        ctx, 
                                        constants.DISK_ATTACH_TO_INSTANCE,
                                        constants.STORAGE_ACCOUNT_KEY
                                        )
        ctx.logger.info("Use storage account {} in DISK_ATTACH_TO_INSTANCE relationship".format(storage_account))

    # Place the vm name in runtime_properties 
    # for relationships DISK_ATTACH_TO_INSTANCE
    ctx.instance.runtime_properties[constants.COMPUTE_KEY] = vm_name

    try:
        for disk in disks:
            json_VM = instance.get_json_from_azure()

            if 'dataDisks' in json_VM['properties']['storageProfile']:
                lun = len(
                          json_VM['properties']['storageProfile']['dataDisks']
                         )
            else:
                lun = 0
                json_VM['properties']['storageProfile']['dataDisks'] = []

            uri = "http://{}.blob.core.windows.net/{}-vhds/{}.vhd".format(
                        storage_account,
                        vm_name,
                        disk['name']
                        )

            if disk['attach']:
                createOption = 'attach'
            else:
                createOption = 'empty'

            json_disk = {"name": disk['name'], 
                         "diskSizeGB": disk['size'], 
                         "lun": lun,
                         "vhd": { "uri" : uri },
                         "caching": disk['caching'],
                         "createOption": createOption
                         }

            json_VM['properties']['storageProfile']['dataDisks'].append(
                                                                json_disk
                                                                )


            ctx.logger.info(('Attaching disk {} on lun {} ' + 
                             'and machine {}.').format(disk['name'],
                                                      lun,
                                                      vm_name
                                                      )
                            )
            connection.AzureConnectionClient().azure_put(
                        ctx,
                        ("subscriptions/{}/resourcegroups/{}/" +
                        "providers/Microsoft.Compute" +
                        "/virtualMachines/{}" +
                        "?validating=true&api-version={}").format(
                                   subscription_id,
                                   resource_group_name,
                                   vm_name,
                                   api_version
                       ),
                       json=json_VM
                       )

            utils.wait_status(ctx, 'instance', constants.SUCCEEDED)

    except utils.WindowsAzureError as e:
    # Do not interrup deployment if maximum number of disks has been reached
        if "The maximum number of data disks" in e.message:
            ctx.logger.warning("{}".format(e.message))
            pass
        else:
            raise e
    except NonRecoverableError as e:
        ctx.logger.error(
                'Machine has failed, check if disks do not already exist.'
                )
        ctx.logger.info('Cancelling worflow.')
        raise e

