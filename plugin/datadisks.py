from plugin import (utils,
                    constants,
                    instance,
                    connection
                    )

from cloudify import ctx
from cloudify.decorators import operation

@operation
def create(**_):
    utils.validate_node_property(constants.SUBSCRIPTION_KEY, 
                                 ctx.node.properties)
    utils.validate_node_property(constants.DISKS_KEY, ctx.node.properties)
    utils.validate_node_property(constants.COMPUTE_KEY, ctx.node.properties)
    utils.validate_node_property(constants.STORAGE_ACCOUNT_KEY, 
                                 ctx.node.properties)
    utils.validate_node_property(constants.RESOURCE_GROUP_KEY, 
                                 ctx.node.properties)
    
    subscription_id = ctx.node.properties[constants.SUBSCRIPTION_KEY]
    vm_name = ctx.node.properties[constants.COMPUTE_KEY]
    storage_account = ctx.node.properties[constants.STORAGE_ACCOUNT_KEY]
    disks = ctx.node.properties[constants.DISKS_KEY]
    resource_group_name = ctx.node.properties[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    ctx.logger.info('Create datadisk')


    try:
        for disk in disks:
            json_VM = instance.get_json_from_azure()
            ctx.logger.debug(json_VM)
            if 'dataDisks' in json_VM['properties']['storageProfile']:
                lun = len(json_VM['properties']['storageProfile']['dataDisks'])
            else:
                lun = 0
                json_VM['properties']['storageProfile']['dataDisks'] = []

            uri = "http://{}.blob.core.windows.net/vhds/{}".format(
                        ctx.node.properties[constants.STORAGE_ACCOUNT_KEY],
                        disk['name']
                        )

            json_disk = {"name": disk['name'], 
                         "diskSizeGB": disk['size'], 
                         "lun": lun,
                         "vhd": { "uri" : uri },
                         "caching": disk['caching'],
                         "createOption":"Empty" 
                        }

            json_VM['properties']['storageProfile']['dataDisks'].append(json_disk)

            ctx.logger.debug(json_VM)

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

    except utils.WindowsAzureError as e:
    # Do not interrup deployment if maximum number of disks has been reached
        if "The maximum number of data disks" in e.message:
            ctx.logger.info("{}".format(e.message))
            pass

    utils.wait_status(ctx, 'instance', constants.UPDATING)
