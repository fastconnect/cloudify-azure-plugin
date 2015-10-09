************
Plugin types
************

.. contents::
    :local:
    :depth: 3

Nodes
=====

cloudify.azure.nodes.ResourceGroup
----------------------------------

Derived From: *cloudify.nodes.Root*

Properties:
^^^^^^^^^^^

* **resource_group_name:** Indicates the name of the resource group to create
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the resource group.
* cloudify.interfaces.lifecycle.delete deletes the resource group.

cloudify.azure.nodes.AvailabilitySet
------------------------------------

Derived From: *cloudify.nodes.Root*

Properties:
^^^^^^^^^^^

* **availability_set_name:** Indicates the name of the availability set to create
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the availability set.
* cloudify.interfaces.lifecycle.delete deletes the availability set.

Attributes:
^^^^^^^^^^^

The availability set name and id are available in the runtime properties of the node.

cloudify.azure.nodes.StorageAccount
-----------------------------------

Derived From: *cloudify.nodes.Root*

Properties:
^^^^^^^^^^^

* **storage_account_name:** Indicates the name of the storage account to create
* **account_type:** account_type possible [Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS, Premium_LRS]
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the storage account.
* cloudify.interfaces.lifecycle.delete deletes the storage account.

Attributes:
^^^^^^^^^^^

The storage account name is available in the runtime properties of the node.

cloudify.azure.nodes.Network
----------------------------

Derived From: *cloudify.nodes.Network*

Properties:
^^^^^^^^^^^

* **virtual_network_name:** Indicates the name of the virtual network to create.
* **virtual_network_address_prefix:** the CIDR (ie. 10.0.0.0/16) to place in the network.
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the virtual network.
* cloudify.interfaces.lifecycle.delete deletes the virtual network.

Attributes:
^^^^^^^^^^^

The virtual network name is available in the runtime properties of the node.

cloudify.azure.nodes.Subnet
---------------------------

Derived From: *cloudify.nodes.Network*

Properties:
^^^^^^^^^^^

* **subnet_name:** Indicates the name of the subnet to create.
* **subnet_address_prefix:** the CIDR (ie. 10.0.1.0/24) to place in the subnet according to its network (see cloudify.azure.relationships.subnet_connected_to_network).
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the subnet.
* cloudify.interfaces.lifecycle.delete deletes the subnet.

Attributes:
^^^^^^^^^^^

Thesubnet name is available in the runtime properties of the node.

cloudify.azure.nodes.NetworkInterfaceCard
-----------------------------------------

Derived From: *cloudify.nodes.Root*

Properties:
^^^^^^^^^^^

* **network_interface_name:** Indicates the name of the network interface card to create.
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the network interface card.
* cloudify.interfaces.lifecycle.delete deletes the network interface card.

Attributes:
^^^^^^^^^^^

The network interface card name is available in the runtime properties of the node.

cloudify.azure.nodes.PublicIP
-----------------------------

Derived From: *cloudify.nodes.VirtualIP*

Properties:
^^^^^^^^^^^

* **public_ip_name:** Indicates the name of the public IP to create.
* **public_ip_allocation_method:** the allocation method (only "Dynamic" supported right now).
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the public IP.
* cloudify.interfaces.lifecycle.delete deletes the public IP.

Attributes:
^^^^^^^^^^^

The public IP name is available in the runtime properties of the node.

cloudify.azure.nodes.Datadisks
------------------------------

Derived From: *cloudify.nodes.Root*

Properties:
^^^^^^^^^^^

* **compute_name:** Indicates the name of the compute to create.
* **storage_account_name:** the storage account name where the disks are stored.
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the datadisks.
 
cloudify.azure.nodes.Instance
-----------------------------

Derived From: *cloudify.nodes.Compute*

Properties:
^^^^^^^^^^^

* **publisher_name:** the editor of the machine to deploy (Canonical).
* **offer:** the machine to deploy (UbuntuServer).
* **sku:** the OS version (14.04.3-LTS).
* **version:** the version build (default: latest).
* **flavor_id:** the size of the machine (Standard-A1).
* **compute_name:** the name of the machine.
* **storage_account_name:** the name of the storage account.
* **compute_user:** the default user on the machine.
* **compute_password:** the password of the user.
* **public_key:** the public key to place in ~/.ssh/agent_key.pem
* **azure_config:** describes the configuration to use to use the Azure API. Outside a blueprint manager, you do not need to set this.

Mapped Operations:
^^^^^^^^^^^^^^^^^^

* cloudify.interfaces.lifecycle.create creates the instance.
* cloudify.interfaces.lifecycle.start starts the instance.
* cloudify.interfaces.lifecycle.stop stops the instance.
* cloudify.interfaces.lifecycle.delete deletes the instance.

Attributes:
^^^^^^^^^^^

The privae IP is available in the runtime properties of the node.
Relationships

Azure configuration
-------------------

This node is used in blueprint manager to set azure credentials.

Derived From: *cloudify.nodes.Root*

Properties:
^^^^^^^^^^^

* **azure_config:**
    * **username:** the user id to log in Azure API.
    * **password:** the password to use to log in.
    * **subscription_id:** the id of the subscription where the resources will be created.
    * **resource_group_name:** the resource group of the manager.
    * **location:** the location of the manager.

All resources deployed through this manager will be created in the resource group definde in azure_config. The location is also set globally.

Relationships
=============

cloudify.azure.relationships.storage_account_contained_in_resource_group
------------------------------------------------------------------------

The relationship to use to place a storage account within a resource group.

cloudify.azure.relationships.availability_set_contained_in_resource_group
-------------------------------------------------------------------------

The relationship to use to place an availability set within a resource group.

cloudify.azure.relationships.network_contained_in_resource_group
----------------------------------------------------------------

The relationship to use to place a network within a resource group.

cloudify.azure.relationships.subnet_connected_to_network
--------------------------------------------------------

The relationship to use to place a subnet within a network.

cloudify.azure.relationships.nic_connected_to_subnet
----------------------------------------------------

The relationship to use to place a nic within a subnet.

cloudify.azure.relationships.nic_connected_to_public_ip
-------------------------------------------------------

The relationship to use to set a public IP in a nic.

cloudify.azure.relationships.public_ip_contained_in_resource_group
------------------------------------------------------------------

The relationship to use to place a public ip within a resource group.

cloudify.azure.relationships.instance_contained_in_resource_group
-----------------------------------------------------------------

The relationship to use to place an instance within a resource group.

cloudify.azure.relationships.instance_contained_in_availability_set
-------------------------------------------------------------------

The relationship to use to place an instance within an availability set.

cloudify.azure.relationships.instance_depends_on_storage_account
----------------------------------------------------------------

The relationship to use to set a storage account for an instance.

cloudify.azure.relationships.instance_connected_to_nic
------------------------------------------------------

The relationship to use to set a nic for an instance.

cloudify.azure.relationships.disk_attach_to_instance
----------------------------------------------------

The relationship to use to place disks within an instance.

