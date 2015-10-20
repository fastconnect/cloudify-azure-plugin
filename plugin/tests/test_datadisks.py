# -*- coding: utf-8 -*-
import test_utils
import testtools
import test_mockcontext
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    storage,
                    network,
                    subnet,
                    public_ip,
                    nic,
                    datadisks,
                    instance
                    )

from test_mockcontext import MockRelationshipContext
from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

class TestDatadisks(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))
    
    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init','')
        ctx.logger.info("BEGIN test datadisk number "\
                                + self.__random_id)   
        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE ressource_group")
        resource_group.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group", 
                          constants.SUCCEEDED, timeout=600)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE storage account")
        ctx.node.properties[constants.ACCOUNT_TYPE_KEY] = "Standard_LRS"
        storage.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "storage",constants.SUCCEEDED, timeout=600)

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY] = \
            "10.0.0.0/16"
        network.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network",constants.SUCCEEDED, timeout=600)

        ctx.logger.info("CREATE subnet")
        current_ctx.set(ctx=ctx)

        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] = "10.0.1.0/24"
        ctx.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] =\
            "diskvirtualnetwork_test" + self.__random_id

        subnet.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, timeout=600)
      
        ctx.logger.info("CREATE NIC")
        current_ctx.set(ctx=ctx)
       
        nic.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, timeout=600)

        
    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del','')

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE ressource_group")
        resource_group.delete(ctx=ctx)

 
    @classmethod 
    def mock_ctx(self, test_name, disk):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY: 'diskresource_group_test'+\
                                                self.__random_id,
                constants.VIRTUAL_NETWORK_KEY: 'diskvirtualnetwork_test' +\
                                                self.__random_id,
                constants.SUBNET_KEY: 'disksubnet_test' +\
                                        self.__random_id,
                constants.STORAGE_ACCOUNT_KEY: 'diskstoaccounttest'+\
                                            self.__random_id
            },
            constants.PUBLISHER_KEY: 'Canonical',
            constants.OFFER_KEY: 'UbuntuServer',
            constants.SKU_KEY: '12.04.5-LTS',
            constants.SKU_VERSION_KEY: 'latest',
            constants.FLAVOR_KEY: 'Standard_A1',
            constants.COMPUTE_KEY: test_name + self.__random_id,
            constants.COMPUTE_USER_KEY: test_utils.COMPUTE_USER,
            constants.COMPUTE_PASSWORD_KEY: test_utils.COMPUTE_PASSWORD,
            constants.PUBLIC_KEY_KEY: test_utils.PUBLIC_KEY,
            constants.PRIVATE_KEY_KEY: test_utils.PRIVATE_KEY,
            constants.STORAGE_ACCOUNT_KEY: 'diskstoaccounttest'+\
                                            self.__random_id,
            constants.CREATE_OPTION_KEY:'FromImage',
            constants.RESOURCE_GROUP_KEY: 'diskresource_group_test'+\
                                            self.__random_id,
            constants.VIRTUAL_NETWORK_KEY: 'diskvirtualnetwork_test'+\
                                            self.__random_id,
            constants.SUBNET_KEY: 'disksubnet_test'+\
                                    self.__random_id,
            constants.NETWORK_INTERFACE_KEY: 'disknic_test'+\
                                                self.__random_id,
            constants.DISKS_KEY: disk,
            'resources_prefix': 'diskprefix',
            constants.DELETABLE_KEY: True

        }
        test_runtime = {
            constants.PUBLIC_IP_KEY: 'diskpublic_ip_test'+\
                                    self.__random_id,
            constants.VIRTUAL_NETWORK_KEY: 'diskvirtualnetwork_test'+\
                                            self.__random_id,
            constants.NETWORK_INTERFACE_KEY: 'disknic_test'+\
                                            self.__random_id,
            constants.COMPUTE_KEY: test_name + self.__random_id
        }

        test_relationships = [
            {
                'node_id': 'test',
                'relationship_type': constants.SUBNET_CONNECTED_TO_NETWORK,
                'relationship_properties': \
                {
                    constants.VIRTUAL_NETWORK_KEY:\
                 'diskvirtualnetwork_test' + self.__random_id
                }
            },
            {
                'node_id': 'test',
                'relationship_type': constants.NIC_CONNECTED_TO_SUBNET,
                'relationship_properties':\
                    {
                        constants.SUBNET_KEY:\
                            'disksubnet_test' + self.__random_id,
                        constants.VIRTUAL_NETWORK_KEY:\
                         'diskvirtualnetwork_test' + self.__random_id
                     }
            },
            {
                'node_id': 'test',
                'relationship_type': constants.INSTANCE_CONNECTED_TO_NIC,
                'relationship_properties':\
                    {
                        constants.NETWORK_INTERFACE_KEY:\
                            'disknic_test' + self.__random_id
                    }
            },
            {
                'node_id': 'test',
                'relationship_type':\
                    constants.DISK_ATTACH_TO_INSTANCE,
                'relationship_properties': \
                {
                    constants.COMPUTE_KEY: \
                        test_name + self.__random_id,
                    constants.STORAGE_ACCOUNT_KEY:\
                        'diskstoaccounttest' + self.__random_id,
                }
            }
        ]

        return test_mockcontext.MockCloudifyContextRelationships(
            node_id='test',
            properties=test_properties,
            runtime_properties=test_runtime,
            relationships=test_relationships
        )

    def test_create_datadisk(self):
        disk = [{'name': 'disk_1',
                 'size': 100,
                 'deletable': False,
                 'caching': 'None'
               }]

        test_name = 'test-create-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name)) 

        instance.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance', constants.SUCCEEDED, timeout=900)

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        ctx.logger.debug(json_VM)

        self.assertIsNotNone(json_VM['properties'][
                                        'storageProfile']['dataDisks'])
        
        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertEqual(disk[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disk[0]['caching'], disks_vm[0]['caching'])
        self.assertEqual(disk[0]['size'], disks_vm[0]['diskSizeGB'])

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name)) 
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

    def test_create_dataDisks(self):
        disks = [{'name': 'disks_1',
                  'size': 100,
                  'deletable': False,
                  'caching': 'None'
                },{'name': 'disks_2',
                   'size': 200,
                   'deletable': False,
                   'caching': 'ReadWrite'
                }]

        test_name = 'test-create-datadisks'
        ctx = self.mock_ctx(test_name, disks)
        current_ctx.set(ctx=ctx)

        ctx.logger.info("BEGIN create VM test: {}".format(test_name))
        instance.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, timeout=900)

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        self.assertIsNotNone(json_VM['properties'][
                                        'storageProfile']['dataDisks'])

        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertEqual(disks[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disks[0]['size'], disks_vm[0]['diskSizeGB'])
        self.assertEqual(disks[0]['caching'], disks_vm[0]['caching'])

        self.assertEqual(disks[1]['name'], disks_vm[1]['name'])
        self.assertEqual(disks[1]['size'], disks_vm[1]['diskSizeGB'])
        self.assertEqual(disks[1]['caching'], disks_vm[1]['caching'])

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance',
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

    def test_create_too_much_datadisks(self):
        disks = [{'name': 'much_disks_1',
                  'size': 100,
                  'deletable': False,
                  'caching': 'None'
                },{'name': 'much_disks_2',
                   'size': 200,
                   'deletable': False,
                   'caching': 'ReadWrite'
                },{'name': 'much_disks_3',
                   'size': 200,
                   'deletable': False,
                   'caching': 'ReadOnly'
                }]

        test_name = 'test-create-too-much-datadisks'
        ctx = self.mock_ctx(test_name , disks)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name)) 

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance', timeout=900)

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        self.assertIsNotNone(json_VM['properties'][
                                        'storageProfile']['dataDisks'])

        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertNotEqual(len(disks), len(disks_vm))

        self.assertEqual(disks[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disks[0]['size'], disks_vm[0]['diskSizeGB'])
        self.assertEqual(disks[0]['caching'], disks_vm[0]['caching'])

        self.assertEqual(disks[1]['name'], disks_vm[1]['name'])
        self.assertEqual(disks[1]['size'], disks_vm[1]['diskSizeGB'])
        self.assertEqual(disks[1]['caching'], disks_vm[1]['caching'])

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

    def test_fail_create_datadisk(self):
        # Disks are limited to a maximum of 1TB
        disk = [{'name': 'disk_fail_1',
                 'size': 5000,
                 'deletable': True,
                 'caching': 'None'
               }]

        test_name = 'test-fail-create-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name)) 

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance',timeout=900)

        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
                          datadisks.create,
                          ctx=ctx
                          )

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name)) 
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass


    def test_attach_datadisk(self):
        disk = [{'name': 'attach_disk',
                  'size': 100,
                  'deletable': False,
                  'caching': 'None'
                }]

        test_name = 'test-attach-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance', timeout=900)

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

        test_name = 'test-attach-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        ctx.logger.debug(json_VM)

        self.assertIsNotNone(json_VM['properties'][
                                        'storageProfile']['dataDisks'])
        
        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertEqual(disk[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disk[0]['caching'], disks_vm[0]['caching'])
        self.assertEqual(disk[0]['size'], disks_vm[0]['diskSizeGB'])
        
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

    def test_datadisk_in_storage_account(self):
        disk = [{'name': 'attach_disk',
                  'size': 100,
                  'deletable': False,
                  'caching': 'None'
                }]

        test_name = 'test-datadisk-in-storage-account'
        ctx = self.mock_ctx(test_name, disk)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE storage account")
        ctx.node.properties[constants.ACCOUNT_TYPE_KEY] = "Standard_LRS"
        ctx.node.properties[constants.STORAGE_ACCOUNT_KEY] = \
            "storageaccountdisk" + self.__random_id
        storage.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "storage",constants.SUCCEEDED, timeout=600)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))

        instance.create(ctx=ctx)
        
        ctx.instance.relationships.append(
                    MockRelationshipContext(
                                'test',
                                {constants.STORAGE_ACCOUNT_KEY: \
                                       'storageaccountdisk' + self.__random_id
                                }, 
                                constants.DISK_CONTAINED_IN_STORAGE_ACCOUNT
                    )
        )
                                            
        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance',timeout=900)

        jsonInstance = instance.get_json_from_azure(ctx=ctx)

        self.assertIn('storageaccountdisk' + self.__random_id,
                      jsonInstance['properties'
                                   ]['storageProfile'
                                     ]['dataDisks'][0]['vhd']['uri']
                      )

        ctx.logger.info('Disks are located in {}.'.format(
                                    'storageaccountdisk' + self.__random_id,
                                    )
                        )

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE storage account")
        ctx.node.properties[constants.ACCOUNT_TYPE_KEY] = "Standard_LRS"
        ctx.node.properties[constants.STORAGE_ACCOUNT_KEY] = \
            "storageaccountdisk" + self.__random_id
        storage.delete(ctx=ctx)
        

    def test_delete_datadisk(self):
        disk = [{'name': 'delete_disk',
                  'size': 100,
                  constants.DELETABLE_KEY: True,
                  'caching': 'None'
                },{'name': 'delete_disk_2',
                  'size': 100,
                  constants.DELETABLE_KEY: False,
                  'caching': 'None'
                }]

        test_name = 'test-delete-datadisk'
        ctx = self.mock_ctx(test_name, disk)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))
        instance.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance',timeout=900)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', 
                              constants.DELETING, timeout=900)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("BEGIN delete datadisk test: {}".format(
                                        disk[0]['name']
                                        )
                        )
        current_ctx.set(ctx=ctx)
        datadisks.delete(ctx=ctx)
        
        list  = datadisks._get_datadisks_from_storage(ctx)
        self.assertFalse(datadisks._is_datadisk_exists(
                                        list,
                                        disk[0]['name']
                                        )
                        )
        ctx.logger.info("Disk {} has been deleted.".format(disk[0]['name']))

        self.assertTrue(datadisks._is_datadisk_exists(
                                        list, 
                                        disk[1]['name']
                                        )
                        )
        ctx.logger.info("Datadisk {} still exists.".format(disk[1]['name']))
