.. _here: http://getcloudify.org/guide/3.2/plugin-windows-agent-installer.html

********************
Custom VHDs on Azure
********************

You are allowed to upload customized images on Azure. This plugin allows you to specify an uri when you want to start an instance with the bootable VHD.
If you do not know about custom images, and how to upload a VHD on Azure, you can follow this guide (even if the API uses ASM, the process is strictly similar):

https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-create-upload-vhd-windows-server/

.. attention:: If you need to start a Windows VM, using a custom VHD is required. Eventually, Windows VM on Azure cannot be customized at startup. Hence, you need to create a Windows VHD with Python 2.7 installed, and a configured WinRM. Check `here`_  for more information.

.. attention:: You *MUST* upload the custom VHD on the *SAME* storage account the VM is linked.

.. attention:: If you want to start a custom Linux, you have to upload the public key *BEFORE* you put the VHD on Azure.

****
Tips
****

You should consider, in accordance with the documentation of Cloudify, to bootstrap a manager on at least Standard-A2.

****************************
Known Limitations (sprint 7)
****************************

* Main resources (resource group, storage account, network, subnet) are fixed by the manager.
* Only one PIP can be attached to one NIC.
* You cannot choose the name of the OS disk, the chosen pattern is "vmname_storageaccountname.vhd".
* You cannot choose the name of the container within the storage account, the chosen pattern is "vmname-vhds".
* DO NOT USE multi-nic instance for now:
    * You cannot set a multi-nic instance on 2 different virtual-network.
    * You cannot set a public IP on a multi-nic instance.
    * You cannot connect a nic to subnet other than the one give by the provider context.

*******************
Future improvements
*******************

* Allow the creation of more than one subnet at boostrap.
* Implement keys vault (TBD).
* Allow network creation for application.
* Implement a complete management of blobs and containers.
* Manage the case when a custom VHD is placed in a different storage account.
  