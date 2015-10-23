# -*- coding: utf-8 -*-
import testtools
import time
import test_utils
import test_mockcontext
import inspect
import threading
import Queue
import random


from plugin import (utils,
                    constants,
                    resource_group,
                    availability_set,
                    public_ip,
                    nic,
                    network,
                    subnet,
                    storage,
                    instance
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError
from unittest import skip

TIME_DELAY = 20

class TestInstance(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))
 
    @classmethod
    def setUpClass(self):     
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test instance number " + self.__random_id)
        
        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE resource_group")
        resource_group.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group", constants.SUCCEEDED, 600)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE storage account")
        ctx.node.properties[constants.ACCOUNT_TYPE_KEY] = "Standard_LRS"
        storage.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "storage",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE subnet")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] = "10.0.1.0/24"
        ctx.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] =\
            "instancevirtualnetwork_test" + self.__random_id

        subnet.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, 600)
      
        ctx.logger.info("CREATE NIC")
        current_ctx.set(ctx=ctx)
        nic.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)
        
    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE resource_group")
        resource_group.delete(ctx=ctx)
 
    @classmethod 
    def mock_ctx(self, test_name, id=None):
        """ Creates a mock context for the instance
            tests
        """
        if id != None:
            nic_name = 'instance_nic_test_{}_{}'.format(self.__random_id, id)
        else:
            nic_name = 'instance_nic_test_{}'.format(self.__random_id)

        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY:\
                    'instanceresource_group_test' + self.__random_id,
                constants.STORAGE_ACCOUNT_KEY:\
                    'instancestoacount' + self.__random_id,
                constants.VIRTUAL_NETWORK_KEY:\
                    'instancevirtualnetwork_test' + self.__random_id,
                constants.SUBNET_KEY:\
                    'instancesubnet_test' + self.__random_id,
            },
            constants.IMAGE_KEY: {
            constants.PUBLISHER_KEY: 'Canonical',
            constants.OFFER_KEY: 'UbuntuServer',
            constants.SKU_KEY: '12.04.5-LTS',
                constants.SKU_VERSION_KEY: 'latest'
            },
            constants.FLAVOR_KEY: 'Standard_A1',
            constants.COMPUTE_KEY: test_name + self.__random_id,
            constants.COMPUTE_USER_KEY: test_utils.COMPUTE_USER,
            constants.COMPUTE_PASSWORD_KEY: test_utils.COMPUTE_PASSWORD,
            constants.PUBLIC_KEY_KEY: test_utils.PUBLIC_KEY,
            constants.PRIVATE_KEY_KEY: test_utils.PRIVATE_KEY,
            constants.STORAGE_ACCOUNT_KEY: 'instancestoacount' + self.__random_id,
            constants.CREATE_OPTION_KEY:'FromImage',
            constants.RESOURCE_GROUP_KEY:\
                'instanceresource_group_test' + self.__random_id,
            constants.AVAILABILITY_SET_KEY:\
                'instanceavailability_set_test' + self.__random_id,
            constants.VIRTUAL_NETWORK_KEY:\
                'instancevirtualnetwork_test' + self.__random_id,
            constants.SUBNET_KEY:\
                'instancesubnet_test' + self.__random_id,
            'resources_prefix': 'instanceprefix',
            constants.NETWORK_INTERFACE_KEY: nic_name,
            constants.DELETABLE_KEY: True
        }

        test_runtime = {
            'not': 'empty'
        }

        test_relationships = [
            {
                'node_id': 'test',
                'relationship_type': constants.SUBNET_CONNECTED_TO_NETWORK,
                'relationship_properties': {
                    constants.VIRTUAL_NETWORK_KEY:\
                        'instancevirtualnetwork_test' + self.__random_id
                }
            },
            {
                'node_id': 'test',
                'relationship_type': constants.NIC_CONNECTED_TO_SUBNET,
                'relationship_properties': {
                        constants.SUBNET_KEY:\
                            'instancesubnet_test' + self.__random_id,
                        constants.VIRTUAL_NETWORK_KEY:\
                            'instancevirtualnetwork_test' + self.__random_id
                     }
            },
            {
                'node_id': 'test',
                'relationship_type': constants.INSTANCE_CONNECTED_TO_NIC,
                'relationship_properties': {
                        constants.NETWORK_INTERFACE_KEY: nic_name,
                        constants.NIC_PRIMARY_KEY: False
                    }
            }
        ]

        return test_mockcontext.MockCloudifyContextRelationships(node_id='test',
            properties=test_properties,
            runtime_properties=test_runtime,
            relationships=test_relationships
        )

    def setUp(self):
        super(TestInstance, self).setUp()


    def tearDown(self):
        super(TestInstance, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create_instance(self):
        ctx = self.mock_ctx('testcreateinstance')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(ctx.instance.id))
        ctx.logger.info("create VM") 

        instance.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create VM test")

    def test_storage_relationship_instance(self):
        ctx = self.mock_ctx('teststorelainstance')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN storage relationship VM test: {}".format(ctx.instance.id))

        ctx.instance.relationships.append(test_mockcontext.MockRelationshipContext(node_id='test',
            runtime_properties={
                constants.STORAGE_ACCOUNT_KEY:\
                     ctx.node.properties[constants.STORAGE_ACCOUNT_KEY]
            },
            type=constants.INSTANCE_CONNECTED_TO_STORAGE_ACCOUNT)
        )

        ctx.logger.info("create VM")
        instance.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create VM test")

    def test_add_availability_set_instance(self):
        ctx = self.mock_ctx('testaddavailabilityinstance')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN add availability set VM test: {}".format(ctx.instance.id))

        ctx.logger.info("create availability_set")
        self.assertEqual(200, availability_set.create(ctx=ctx))
        ctx.logger.debug("availability_set_id = {}".format(
            ctx.instance.runtime_properties[constants.AVAILABILITY_ID_KEY]))

        ctx.instance.relationships.append(test_mockcontext.MockRelationshipContext(node_id='test',
            runtime_properties={
                constants.AVAILABILITY_ID_KEY:\
                     ctx.instance.runtime_properties[constants.AVAILABILITY_ID_KEY]
            },
            type=constants.INSTANCE_CONTAINED_IN_AVAILABILITY_SET)
        )

        ctx.logger.info("create VM")
        instance.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("test instance is in availability_set")
        current_ctx.set(ctx=ctx)
        json = instance.get_json_from_azure(ctx=ctx)
        self.assertIsNotNone(json['properties']['availabilitySet'])
        self.assertEqual(str(json['properties']['availabilitySet']['id']).lower(),
            str(ctx.instance.runtime_properties[constants.AVAILABILITY_ID_KEY]).lower()
        )

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("delete availability_set")
        self.assertEqual(200, availability_set.delete(ctx=ctx))

        ctx.logger.info("END create VM test")

    def test_delete_instance(self):    
        ctx = self.mock_ctx('testdeleteinstance')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test")
    
        ctx.logger.info("create VM")    
        instance.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)
        
        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END delete VM test")

    def test_conflict_instance(self):
        ctx = self.mock_ctx('testconflictinstance')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict VM test")

        ctx.logger.info("create VM")
        instance.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("VM creation conflict")
        self.assertRaises(utils.WindowsAzureError,
                         instance.create,
                         ctx=ctx
                         )

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        current_ctx.set(ctx=ctx)
        ctx.logger.info("check vm provisionning state in a deleted machine")
        self.assertRaises(
                          utils.WindowsAzureError,
                          instance.get_provisioning_state,
                          ctx=ctx
                          )

        ctx.logger.info("delete VM conflict")
        self.assertEqual(204, instance.delete(ctx=ctx))
        ctx.logger.info("END conflict VM test")
        time.sleep(TIME_DELAY)
     
    def test_stop(self):
        ctx = self.mock_ctx('teststop')
        current_ctx.set(ctx=ctx)

    def test_concurrent_create_instance(self):
        ctx1 = self.mock_ctx('testconcurrentcreate1', id=1)
        ctx2 = self.mock_ctx('testconcurrentcreate2', id=2)
        ctx1.logger.info("BEGIN concurrent create VM 1 test")
        ctx2.logger.info("BEGIN concurrent create VM 2 test")

        ctx1.logger.info("CREATE nic 1")
        current_ctx.set(ctx=ctx1)
        nic.create(ctx=ctx1)
        current_ctx.set(ctx=ctx1)
        utils.wait_status(ctx1, "nic",constants.SUCCEEDED, 600)

        ctx2.logger.info("CREATE nic 2")
        current_ctx.set(ctx=ctx2)
        nic.create(ctx=ctx2)
        current_ctx.set(ctx=ctx2)
        utils.wait_status(ctx2, "nic",constants.SUCCEEDED, 600)

        def create_vm(lctx):
            instance.create(ctx=lctx)
            return
        vm1 = threading.Thread(target=create_vm, args=(ctx1,))
        vm2 = threading.Thread(target=create_vm, args=(ctx2,))

        ctx1.logger.info("create VM 1")
        vm1.start()

        ctx2.logger.info("create VM 2")
        vm2.start()

        vm1.join()
        vm2.join()

        ctx1.logger.info("check VM 1 status")
        ctx2.logger.info("check VM 2 status")
        status_vm1 = constants.CREATING
        status_vm2 = constants.CREATING
        while bool(status_vm1 == constants.CREATING or status_vm2 == constants.CREATING) :
            current_ctx.set(ctx=ctx1)
            status_vm1 = instance.get_provisioning_state(ctx=ctx1)
            current_ctx.set(ctx=ctx2)
            status_vm2 = instance.get_provisioning_state(ctx=ctx2)
            time.sleep(TIME_DELAY)

        ctx1.logger.info("check VM 1 creation success")
        self.assertEqual(constants.SUCCEEDED, status_vm1)

        ctx2.logger.info("check VM 2 creation success")
        self.assertEqual(constants.SUCCEEDED, status_vm2)

        ctx1.logger.info("delete VM 1")
        self.assertEqual(202, instance.delete(ctx=ctx1))

        ctx2.logger.info("delete VM 2")
        self.assertEqual(202, instance.delete(ctx=ctx2))

        current_ctx.set(ctx=ctx1)
        ctx1.logger.info("DELETE nic 1")
        nic.delete(ctx=ctx1)

        current_ctx.set(ctx=ctx2)
        ctx2.logger.info("DELETE nic 2")
        nic.delete(ctx=ctx2)

        ctx1.logger.info("END concurrent create VM 1 test")
        ctx2.logger.info("END concurrent create VM 2 test")

    def test_concurrent_delete_instance(self):
        ctx1 = self.mock_ctx('testconcurrentdelete1', id=1)
        ctx2 = self.mock_ctx('testconcurrentdelete2', id=2)

        ctx1.logger.info("BEGIN concurrent delete VM 1 test")
        ctx2.logger.info("BEGIN concurrent delete VM 2 test")

        ctx1.logger.info("CREATE nic 1")
        current_ctx.set(ctx=ctx1)
        nic.create(ctx=ctx1)
        current_ctx.set(ctx=ctx1)
        utils.wait_status(ctx1, "nic",constants.SUCCEEDED, 600)

        ctx2.logger.info("CREATE nic 2")
        current_ctx.set(ctx=ctx2)
        nic.create(ctx=ctx2)
        current_ctx.set(ctx=ctx2)
        utils.wait_status(ctx2, "nic",constants.SUCCEEDED, 600)

        ctx1.logger.info("create VM 1")
        instance.create(ctx=ctx1)

        ctx2.logger.info("create VM 2")
        instance.create(ctx=ctx2)

        ctx1.logger.info("check VM 1 status")
        ctx2.logger.info("check VM 2 status")
        status_vm1 = constants.CREATING
        status_vm2 = constants.CREATING
        while bool(status_vm1 == constants.CREATING or
                   status_vm2 == constants.CREATING) :
            current_ctx.set(ctx=ctx1)
            status_vm1 = instance.get_provisioning_state(ctx=ctx1)
            current_ctx.set(ctx=ctx2)
            status_vm2 = instance.get_provisioning_state(ctx=ctx2)
            time.sleep(TIME_DELAY)

        ctx1.logger.info("check VM 1 creation success")
        self.assertEqual(constants.SUCCEEDED, status_vm1)

        ctx2.logger.info("check VM 2 creation success")
        self.assertEqual(constants.SUCCEEDED, status_vm2)

        def delete_vm(mokctx, queue):
            queue.put(instance.delete(ctx=mokctx))
        queue1 = Queue.Queue()
        queue2 = Queue.Queue()
        vm1 = threading.Thread(target=delete_vm, args=(ctx1,queue1))
        vm2 = threading.Thread(target=delete_vm, args=(ctx2,queue2))

        ctx1.logger.info("delete VM 1")
        vm1.start()

        ctx2.logger.info("delete VM 2")
        vm2.start()

        vm1.join()
        vm2.join()
        
        self.assertEqual(202, queue1.get())
        self.assertEqual(202, queue2.get())

        current_ctx.set(ctx=ctx1)
        ctx1.logger.info("DELETE nic 1")
        nic.delete(ctx=ctx1)

        current_ctx.set(ctx=ctx2)
        ctx2.logger.info("DELETE nic 2")
        nic.delete(ctx=ctx2)

        ctx1.logger.info("END concurrent delete VM 1 test")
        ctx2.logger.info("END concurrent delete VM 2 test")


    def test_nicInUse_instance(self):
        ctx1 = self.mock_ctx('testnicinuse')
        ctx2 = self.mock_ctx('testnicinuse2')
        ctx1.logger.info("BEGIN nicInUse test")

        current_ctx.set(ctx=ctx1)
        ctx1.logger.info("create VM")
        instance.create(ctx=ctx1)
        current_ctx.set(ctx=ctx1)
        utils.wait_status(ctx1, "instance",constants.SUCCEEDED, 600)

        ctx1.logger.info("VM creation conflict nicInUse")
        self.assertRaises(utils.WindowsAzureError,
                         instance.create,
                         ctx=ctx2
                         )

        ctx1.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx1))

        current_ctx.set(ctx=ctx1)
        ctx1.logger.info("check vm provisionning state in a deleted machine")
        self.assertRaises(
                          utils.WindowsAzureError,
                          instance.get_provisioning_state,
                          ctx=ctx1
                          )

        ctx1.logger.info("END conflict VM test")
        time.sleep(TIME_DELAY)


    def test_get_json_instance(self):
        ctx = self.mock_ctx('testgetjson')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN getjson VM test")

        ctx.logger.info("Creating VM...")
        instance.create(ctx=ctx)

        time.sleep(TIME_DELAY)

        ctx.logger.info("Getting json...")
        current_ctx.set(ctx=ctx)
        jsonVM = instance.get_json_from_azure(ctx=ctx)

        self.assertEqual(jsonVM['name'], ctx.node.properties[constants.COMPUTE_KEY])

        time.sleep(TIME_DELAY)

        ctx.logger.info("Deleting VM...")
        current_ctx.set(ctx=ctx)
        instance.delete(ctx=ctx)
   
    def test_create_windows_instance(self):
        ctx = self.mock_ctx('testwin')
        ctx.node.properties[constants.IMAGE_KEY
                            ][constants.PUBLISHER_KEY] = \
            'MicrosoftWindowsServer'
        ctx.node.properties[constants.IMAGE_KEY
                            ][constants.OFFER_KEY] = 'WindowsServer'
        ctx.node.properties[constants.IMAGE_KEY
                            ][constants.SKU_KEY] = '2012-R2-Datacenter'
        ctx.node.properties[constants.IMAGE_KEY
                            ][constants.WINDOWS_AUTOMATIC_UPDATES_KEY] = True

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create windows VM test")

        ctx.logger.info("Creating VM...")
        instance.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        jsonVM = instance.get_json_from_azure(ctx=ctx)

        self.assertIsNotNone(jsonVM['properties']['osProfile'][
                                    'windowsConfiguration'])
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("delete windows VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create windows VM test")

    @skip("Create test from VHD is not compliant with other instance tests.")
    def test_create_instance_from_vhd(self):
        '''To run this test, you need all the required resource to start a machine
        (resource group, storage account, nic). You then have to upload a valid
        bootable VHD on the storage account. Note the vhd's endpoint and replace 
        MY_URI_VHD by this value.
        Then, you can run the test.
        Note the resource group will not be deleted by the class teardown.
        '''
        ctx = self.mock_ctx('testinstancevhd')
        ctx.node.properties[constants.AZURE_CONFIG_KEY
                            ][constants.RESOURCE_GROUP_KEY] = MY_RESOURCE_GROUP
        ctx.node.properties[constants.AZURE_CONFIG_KEY
                            ][constants.STORAGE_ACCOUNT_KEY] = MY_STORAGE_ACCOUNT
        ctx.node.properties[constants.NETWORK_INTERFACE_KEY] = MY_NIC
        ctx.node.properties[constants.IMAGE_KEY] = {}
        ctx.node.properties[constants.IMAGE_KEY
                            ][constants.OS_URI_KEY] = MY_URI_VHD
        ctx.node.properties[constants.IMAGE_KEY
                            ][constants.OS_TYPE_KEY] = 'Linux'

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(ctx.instance.id))
        ctx.logger.info("create VM") 

        instance.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        current_ctx.set(ctx=ctx)
        jsonVM = instance.get_json_from_azure(ctx=ctx)

        self.assertEqual(jsonVM['properties']['storageProfile'
                                              ]['osDisk']['osType'],  
                         ctx.node.properties[constants.IMAGE_KEY
                            ][constants.OS_TYPE_KEY]
                         )

        self.assertEqual(jsonVM['properties']['storageProfile'
                                              ]['osDisk']['image']['uri'],
                         ctx.node.properties[constants.IMAGE_KEY
                            ][constants.OS_URI_KEY]
                         )

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create VM test")

    def test_create_2nic_instance(self):
        ctx = self.mock_ctx('testcreate2nicinstance')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create 2 NIC VM test: {}".format(ctx.instance.id))

        subnet_name = 'instancesubnet_test_2_' + self.__random_id
        nic_name = 'instance_nic_test_2_' + self.__random_id

        ctx.logger.info("create new subnet")
        ctx.node.properties[constants.SUBNET_KEY] = subnet_name
        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] =\
            "10.0.2.0/24"
        current_ctx.set(ctx=ctx)
        subnet.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, 600)

        ctx.logger.info("create second NIC")
        ctx.node.properties[constants.NETWORK_INTERFACE_KEY] = nic_name
        ctx.node.properties[constants.NIC_PRIMARY_KEY] = True
        ctx.node.properties[constants.AZURE_CONFIG_KEY][constants.SUBNET_KEY] = subnet_name
        for relationship in ctx.instance.relationships:
            if relationship.type == constants.NIC_CONNECTED_TO_SUBNET:
                relationship.target.instance.runtime_properties[constants.SUBNET_KEY] = subnet_name
        current_ctx.set(ctx=ctx)
        nic.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)

        ctx.logger.info("create VM")
        ctx.node.properties[constants.FLAVOR_KEY] = 'Standard_A3'
        ctx.instance.relationships.append(test_mockcontext.MockRelationshipContext(node_id='test',
            runtime_properties={
                constants.NETWORK_INTERFACE_KEY: nic_name,
                constants.NIC_PRIMARY_KEY: True
            },
            type=constants.INSTANCE_CONNECTED_TO_NIC)
        )
        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("verify the NIC's number of the instance")
        json = instance.get_json_from_azure()
        self.assertEqual(len(json['properties']['networkProfile']['networkInterfaces']),2)

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create VM test")
