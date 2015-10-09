.. _package: https://fastconnect.org/maven/service/local/repositories/fastconnect/content/fastconnect/cloudify-azure-plugin/cloudify-azure-plugin/0.0.1/cloudify-azure-plugin-0.0.1.zip

**********
User Guide
**********

Introduction
============

This page is a reference to use the Azure plugin for Cloudify 3. The aim is to be able to deploy a Cloudify manager and compatible application on Microsoft Azure.

When you will finish to read this, you will be able to:

* Bootstrap/teardown a Cloudify manager on Azure,
* Create/delete an application,
* Configure a deployment,
* Create/delete required resources (resources groups, availability sets, storage account, datadisks…).

Assumptions
===========

* You have some basics knowledge on Azure, you know what is a resource group, storage account…
* You have some understandings about Cloud (virtual networks, virtual subnets, virtual machines…),
* You know how to use Cloudify 3, and you understand some of its principles (TOSCA, blueprints, manager, agent, plugins…)

Software
========

* Python: 2.7.x
* Cloudify: 3.2.1
* Azure API REST: Azure Resource Manager

Installation
============

Cloudify 3 offers two ways to install plugins: via Cloudify CLI (cfy local --install-plugins) or via pip

We recommend to use pip to install the plugin as the package is not available publicly, you have to download the zip package.
Package

You can download the package here:

`package`_ 

The zip have the following architecture:

* blueprints/
	* compute/
		* manager/
		* nodecellar/
* plugin/
	* tests/
* dev-requirements.txt
* plugin.yaml
* README.md
* setup.py

The blueprints folder contains blueprints example you can use to deploy a manager, a simple compute, or nodecellar application with 2 compute (node-js and mongod).

Plugin references the plugin code and its unit tests.

plugin.yaml presents all the available nodes you can use in your custom blueprints. You can read more information on Azure plugin documentation
Pip install

We assume that you have installed Cloudify CLI 3.2.1, and you are in its virtualenv.

If you have not used the CLI yet, you do not have the fabric plugin installed.

Hence, execute this command before trying to install the plugin (for Cloudify 3.2.1):
pip install https://github.com/cloudify-cosmo/cloudify-fabric-plugin/archive/1.2.1.zip

Once you have installed fabric, you can install the plugin without trouble:
pip install /Where/the/plugin/is/cloudify-azure-plugin-0.0.1.zip
Icon

.. attention:: If you need to upgrade the plugin, be sure to use the --upgrade option for pip.

You are now ready to bootstrap your manager.

Bootstrap
=========

The bootstrap process should not be a problem, check the azure-blueprints-manager.yaml located in the pacakge and the inputs.yaml.template for required inputs.

We recommend for the manager to use at least a Standard-A2 (2 vcpu, 3.5 GiB RAM) flavor. Be sure to have the right access to the API (check with your Azure Admin).

Then, you just need to execute the command:

.. code-block:: shell
	
    cfy bootstrap -p azure-blueprints-manager.yaml -i inputs.yaml

.. attention:: UTF-8 encoding: be sure your files are correctly encoded, as Python 2.7.x may have some trouble with othen encodings.

Your manager is now ready to deploy your applications. Be sure that your blueprints are compatible with the plugin.

___________________________________________________________________________

.. include:: user_guide_migration.rst
