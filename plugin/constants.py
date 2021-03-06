# -*- coding: utf-8 -*-
########
# Copyright (c) 2015 Fastconnect - Atost. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# instance module constants
INSTANCE_STATE_STARTED = 16
INSTANCE_STATE_TERMINATED = 48
INSTANCE_STATE_STOPPED = 80
TIME_DELAY = 10

INSTANCE_REQUIRED_PROPERTIES = [
    'image_id', 'instance_type', 'cloud_service',
    'affinity_group', 'storage_account_url'
]

INSTANCE_INTERNAL_ATTRIBUTES = \
    ['private_dns_name', 'public_dns_name', 'public_ip_address', 'ip']

RUN_INSTANCE_PARAMETERS = {
    'image_id': None, 'key_name': None, 'security_groups': None,
    'user_data': None, 'addressing_type': None,
    'instance_type': 'm1.small', 'placement': None, 'kernel_id': None,
    'ramdisk_id': None, 'monitoring_enabled': False, 'subnet_id': None,
    'block_device_map': None, 'disable_api_termination': False,
    'instance_initiated_shutdown_behavior': None,
    'private_ip_address': None, 'placement_group': None,
    'client_token': None, 'security_group_ids': None,
    'additional_info': None, 'instance_profile_name': None,
    'instance_profile_arn': None, 'tenancy': None, 'ebs_optimized': False,
    'network_interfaces': None, 'dry_run': False
}

CREATING = 'Creating'
UPDATING = 'Updating'
FAILED = 'Failed'
SUCCEEDED = 'Succeeded'
DELETING = 'Deleting'

REQUEST_SUCCEEDED = 'Succeeded'
REQUEST_IN_PROGRESS = 'InProgress'
REQUEST_FAILED = 'Failed'

TOKEN_URL = 'https://login.windows.net/common/oauth2/token'
RESOURCE_CONNECTION_URL = 'https://management.core.windows.net/'
AZURE_API_URL = 'https://management.azure.com'

AZURE_API_VERSION_01 = '2015-01-01'
AZURE_API_VERSION_04_PREVIEW = '2014-04-01-preview'
AZURE_API_VERSION_05_preview = '2015-05-01-preview'
AZURE_API_VERSION_06 = '2015-06-15'

# Do not touch, it represents a client ID used to get access token
APPLICATION_ID = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

# config
NODE_INSTANCE = 'node-instance'
RELATIONSHIP_INSTANCE = 'relationship-instance'

# properties keys
AZURE_CONFIG_KEY = 'azure_config'
SUBSCRIPTION_KEY = 'subscription_id'
USERNAME_KEY = 'username'
PASSWORD_KEY = 'password'
LOCATION_KEY = 'location'

RESOURCE_GROUP_KEY = 'resource_group_name'

STORAGE_ACCOUNT_KEY = 'storage_account_name'
ACCOUNT_TYPE_KEY = 'account_type'

VIRTUAL_NETWORK_KEY = 'virtual_network_name'
VIRTUAL_NETWORK_ADDRESS_KEY = 'virtual_network_address_prefix'
SUBNET_KEY = 'subnet_name'
SUBNET_ADDRESS_KEY = 'subnet_address_prefix'

SECURITY_GROUP_KEY = 'security_group_name'
SECURITY_GROUP_ID_KEY = 'security_group_id'
RULES_KEY = 'rules'
PROTOCOL_KEY = 'protocol'
SOURCE_PORT_KEY = 'sourcePortRange'
DEST_PORT_KEY = 'destinationPortRange'
SOURCE_ADDRESS_KEY = 'sourceAddressPrefix'
DEST_ADDRESS_KEY = 'destinationAddressPrefix'
ACCESS_KEY = 'access'
DIRECTION_KEY = 'direction'

NETWORK_INTERFACE_KEY = 'network_interface_name'
NIC_PRIMARY_KEY = 'primary'

PUBLIC_IP_KEY = 'public_ip_name'

COMPUTE_KEY = 'compute_name'
COMPUTE_USER_KEY = 'compute_user'
COMPUTE_PASSWORD_KEY = 'compute_password'
PUBLIC_KEY_KEY = 'public_key'
PRIVATE_KEY_KEY = 'private_key'
FLAVOR_KEY = 'flavor_id'
IMAGE_KEY = 'image'
PUBLISHER_KEY = 'publisher_name'
OFFER_KEY = 'offer'
SKU_KEY = 'sku'
SKU_VERSION_KEY = 'version'
CREATE_OPTION_KEY = 'create_option'
OS_URI_KEY = 'os_uri'
OS_TYPE_KEY = 'os_type'
DISKS_KEY = 'disks'
WINDOWS_AUTOMATIC_UPDATES_KEY = 'windows_automatic_updates'

AVAILABILITY_SET_KEY = 'availability_set_name'
AVAILABILITY_ID_KEY = 'availability_set_id'

DELETABLE_KEY = 'deletable'

# RELATIONSHIPS KEYS
STORAGE_ACCOUNT_CONTAINED_IN_RESOURCE_GROUP = \
    'cloudify.azure.relationships.storage_account_contained_in_resource_group'
AVAILABILITY_SET_CONTAINED_IN_RESOURCE_GROUP = \
    'cloudify.azure.relationships.availability_set_contained_in_resource_group'
SECURITY_GROUP_CONTAINED_IN_RESOURCE_GROUP = \
    'cloudify.azure.relationships.security_group_contained_in_resource_group'
NETWORK_CONTAINED_IN_RESOURCE_GROUP = \
    'cloudify.azure.relationships.network_contained_in_resource_group'
SUBNET_CONNECTED_TO_NETWORK = \
    'cloudify.azure.relationships.subnet_connected_to_network'
SUBNET_CONNECTED_TO_SECURITY_GROUP = \
    'cloudify.azure.relationships.subnet_connected_to_security_group'
NIC_CONNECTED_TO_SUBNET = \
    'cloudify.azure.relationships.nic_connected_to_subnet'
NIC_CONNECTED_TO_PUBLIC_IP = \
    'cloudify.azure.relationships.nic_connected_to_public_ip'
INSTANCE_CONTAINED_IN_RESOURCE_GROUP = \
    'cloudify.azure.relationships.instance_contained_in_resource_group'
INSTANCE_CONTAINED_IN_AVAILABILITY_SET = \
    'cloudify.azure.relationships.instance_contained_in_availability_set'
INSTANCE_CONNECTED_TO_STORAGE_ACCOUNT = \
    'cloudify.azure.relationships.instance_depends_on_storage_account'
INSTANCE_CONNECTED_TO_NIC = \
    'cloudify.azure.relationships.instance_connected_to_nic'
DISK_ATTACH_TO_INSTANCE = 'cloudify.azure.relationships.disk_attach_to_instance'
DISK_CONTAINED_IN_STORAGE_ACCOUNT = 'cloudify.azure.relationships.disk_contained_in_storage_account'

