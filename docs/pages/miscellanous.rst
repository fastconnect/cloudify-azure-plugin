****
Tips
****

You should consider, in accordance with the documentation of Cloudify, to bootstrap a manager on at least Standard-A2.

****************************
Known Limitations (sprint 5)
****************************

* Main resources (resource group, storage account, network, subnet) are fixed by the manager.
* Datadisks may have a weird behaviour. Azure does not provide a clean way to use datadisks. Eventually, you cannot delete datadisks.
* You may not put more than one NIC per machine.
* Only one PIP can be attached to one NIC.

*******************
Future improvements
*******************

* Improve relationships workflows (datadisks, storage account).
* Allow the creation of more than one subnet at boostrap.
* Implement secutity groups.
* Implement availability sets.
* Implement keys vault (TBD).
  