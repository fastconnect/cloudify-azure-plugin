# -*- coding: utf-8 -*-
from plugin import (utils,
                    constants,
                    instance,
                    connection,
                    storage
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError
import base64
import re
import hmac
import time
import requests
import hashlib
import xml.etree.ElementTree as ET


@operation
def create(**_):
    """Create a data disk. The datadisk can be created in the same
    storage account of the VM, or in its own storage account as
    defined in the blueprint. Within the storage account, the disk
    is contained in a container, its name follows this schema:
    <vm_name>-vhds. All disks are automatically suffixed with .vhd.

    :param ctx: The Cloudify ctx context.
    """
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
        ctx.logger.info(("Use storage account {} in" +  
                        "DISK_CONTAINED_IN_STORAGE_ACCOUNT relationship").
                        format(storage_account)
                        )
    except NonRecoverableError:
        storage_account = utils.get_target_property(
                                        ctx, 
                                        constants.DISK_ATTACH_TO_INSTANCE,
                                        constants.STORAGE_ACCOUNT_KEY
                                        )
        ctx.logger.info(("Use storage account {}" + 
                        "in DISK_ATTACH_TO_INSTANCE relationship").
                        format(storage_account)
                        )

    # Place the vm name and storag account in runtime_properties 
    # It is used to retrieve disks from the storage account
    ctx.instance.runtime_properties[constants.COMPUTE_KEY] = vm_name
    ctx.instance.runtime_properties[constants.STORAGE_ACCOUNT_KEY] = storage_account
    
    # Caching the list of datadisks existing in the storage account
    blobs_name = []
    try:
        blobs_name = _get_datadisks_from_storage(ctx)
    except utils.WindowsAzureError as e:
        ctx.logger.debug('{} == 404: {}'.format(e.code, str(e.code) == '404'))
        if str(e.code) == '404' and 'ContainerNotFound' in e.message :
            ctx.logger.info('A container has not been found, it will be created.')
        else:
            raise e
        

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

            if _is_datadisk_exists(blobs_name, disk['name']):
                ctx.logger.info(('Disk {} already exists,' +  
                                'trying to attach it').format(disk['name']))
                createOption = 'attach'
            else:
                ctx.logger.info('Disk {} does not exist,' + 
                                'creating it.'.format(disk['name'])
                                )
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


@operation
def delete(**_):
    """Delete a data disk.

    :param ctx: The Cloudify ctx context.
    """
    vm_name = ctx.instance.runtime_properties[constants.COMPUTE_KEY]
    storage_account = \
        ctx.instance.runtime_properties[constants.STORAGE_ACCOUNT_KEY]
    disks = ctx.node.properties[constants.DISKS_KEY]
    key = storage.get_storage_keys(ctx)[0]
    timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    container = "{}-vhds".format(vm_name)
    version = "2015-02-21"

    for disk in disks:
        if disk[constants.DELETABLE_KEY]:
            string_to_sign = ("DELETE\n" +
				              "\n" +
				              "\n" + 
				              "\n" +
				              "\n" +
				              "\n" + 
				              "\n" +
				              "\n" +
				              "\n" +
				              "\n" +
				              "\n" + 
				              "\n" +
				              "x-ms-date:{}\n" +
				              "x-ms-version:{}\n" +
				              "/{}/{}/{}.vhd"
				              ).format(timestamp,
                                       version,
                                       storage_account, 
                                       container,
                                       disk['name']
                                       )

            signed_string = hmac.new(key=base64.b64decode(key), 
                                     msg=unicode(string_to_sign, "utf-8"), 
                                     digestmod=hashlib.sha256
                                    )
            header = {'x-ms-date': timestamp,
		              'x-ms-version': version,
		              'Authorization': 'SharedKey {}:{}'.format(
                            storage_account,
                            base64.b64encode(signed_string.digest())
                            )
		            }

            response = requests.delete(("https://{}.blob.core.windows.net/" +
                                       "{}/{}.vhd").format(storage_account,
                                                           container,
                                                           disk['name']
                                                          ),
                                        headers=header
                                       )

            if not re.match(r'(^2+)', '{}'.format(response.status_code)):
                raise utils.WindowsAzureError(
                        response.status_code,
                        response.text
                        )

            ctx.logger.info("Disk has been successfully deleted.")
        else:
            ctx.logger.info(("Disk will not be deleted" + 
                            "thanks to deletable property."))


def _is_datadisk_exists(existing_disks, datadisk_name):
    """Helper to test if a datadisks exists among
    existing disks.

    :param existing_disks: A list that contains the existing 
                           disks within a storage account.
    :param datadisk_name: The name of the disk to test. You do not need to
                          suffix the name with .vhd.
    :return: True if the disk has been found, False either.
    :rtype: Boolean
    """
    return True if (datadisk_name + ".vhd") in existing_disks else False


def _get_datadisks_from_storage(ctx):
    """Helper to retrieve the list of the existing disks within a storage account.
    The storage account used here is the one present in the runtime_properties
    of the disk.

    :param ctx: The Cloudify ctx context.
    :rtype: List
    """
    vm_name = ctx.instance.runtime_properties[constants.COMPUTE_KEY]
    storage_account = \
        ctx.instance.runtime_properties[constants.STORAGE_ACCOUNT_KEY]
    key = storage.get_storage_keys(ctx)[0]
    version = "2015-02-21"
    timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    container = "{}-vhds".format(vm_name)
    string_to_sign = ("GET\n" +
				      "\n" +
				      "\n" + 
				      "\n" +
				      "\n" +
				      "\n" + 
				      "\n" +
				      "\n" +
				      "\n" +
				      "\n" +
				      "\n" + 
				      "\n" +
				      "x-ms-date:{}\n" +
				      "x-ms-version:{}\n" +
				      "/{}/{}\n" +
				      "comp:list\n" +
				      "restype:container" 
				      ).format(timestamp, version, storage_account, container)

    signed_string = hmac.new(key=base64.b64decode(key), 
                             msg=unicode(string_to_sign, "utf-8"), 
                             digestmod=hashlib.sha256
                             )

    header = {'x-ms-date': timestamp,
		      'x-ms-version': version,
		      'Authorization': 'SharedKey {}:{}'.format(
                        storage_account,
                        base64.b64encode(signed_string.digest())
                        )
		     }

    response = requests.get(("https://{}.blob.core.windows.net/{}?" +
                             "restype=container&comp=list").format(
                                                    storage_account,
                                                    container
                                                    ),
                            headers=header
                            )
    
    if not re.match(r'(^2+)', '{}'.format(response.status_code)):
        raise utils.WindowsAzureError(
                    response.status_code,
                    response.text
                    )

    xml_list_blob = ET.fromstring(response.text)
    xml_blobs_name = xml_list_blob.findall("./Blobs/Blob/Name")

    blobs_name = []
    for blob in xml_blobs_name:
        blobs_name.append(blob.text)

    ctx.logger.debug("Blobs names: {} in {}/{}".format(
                            blobs_name,
                            storage_account,
                            container
                            )
                     )
    return blobs_name
