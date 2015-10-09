How-to: migrate an application from Openstack to Azure
======================================================

Structure
---------
We will discuss on how you can easily migrate an application designed to be deployed by Cloudify on Openstack to Azure with this plugin.

We have done a similar migration for the Nodecellar application, you can check its blueprint for a concrete example.
Plugin migration

The first thing you have to do is to reference the plugin. In the imports section of the blueprint, you need to reference the plugin.yaml file. It is required as this file references all plugin types!

You should have something similar:

.. code-block:: yaml

    imports:
      - http://www.getcloudify.org/spec/cloudify/3.2.1/types.yaml
      - plugins/plugin.yaml
      - http://www.getcloudify.org/spec/diamond-plugin/1.2.1/plugin.yaml
      - types/nodecellar.yaml

In this example, we decided to place the file in the subfolder plugins.

.. attention:: You MUST place the zip package (cloudify-azure-plugin.zip) in the plugins subfolder. As Cloudify needs it to deploy the application.

Types migration
---------------

Then, you need to change the types used in the blueprint:

* cloudify.openstack.nodes.Server -> cloudify.azure.nodes.Instance

    * Required input for Azure: publisher_name, offer, sku, version, flavor_id, compute_name, storage_account_name, compute_user, compute_password, public_key

.. hint:: The public key you need to reference corresponds to the private key you have given to the manager.

* cloudify.openstack.nodes.FloatingIP -> cloudify.azure.nodes.PublicIP and a property called 'public_ip_name'
* Delete references to security as it has not been implemented in the plugin yet.

* You need to add Network Interface Card (NIC) to each machine you use:

  .. code-block:: yaml
  
      my_nic:
      type: cloudify.azure.nodes.NetworkInterfaceCard
      properties:
        network_interface_name: "my_nic_name"
    

* The public IP is connected to a NIC, you need to use the relevant relationship in NIC node to make the connection:

  .. code-block:: yaml
  
      relationships:
      - target: my_public_ip
        type: cloudify.azure.relationships.nic_connected_to_public_ip
    

* You also need to connect the NIC to the relevant machine by a relationship:

  .. code-block:: yaml
  
      relationships:
      - target: my_nic
        type: cloudify.azure.relationships.instance_connected_to_nic
    
