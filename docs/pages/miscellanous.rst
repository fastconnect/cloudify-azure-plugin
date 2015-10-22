****
Tips
****

You should consider, in accordance with the documentation of Cloudify, to bootstrap a manager on at least Standard-A2.

****************************
Known Limitations (sprint 5)
****************************

* Main resources (resource group, storage account, network, subnet) are fixed by the manager.
* You may not put more than one NIC per machine.
* Only one PIP can be attached to one NIC.
* You cannot choose the name of the OS disk, the chosen pattern is "vmname_storageaccountname.vhd".
* You cannot choose the name of the container within the storage account, the chosen pattern is "vmname-vhds".

*******************
Future improvements
*******************

* Improve relationships workflows (datadisks, storage account).
* Allow the creation of more than one subnet at boostrap.
* Implement secutity groups.
* Implement availability sets.
* Implement keys vault (TBD).
* Allow network creation for application
  