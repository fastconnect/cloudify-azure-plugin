﻿import testtools
import time
import test_utils
import inspect
import threading
import Queue


from plugin import (utils,
                    constants,
                    resource_group,
                    public_ip,
                    nic,
                    network,
                    storage,
                    instance
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

TIME_DELAY = 20

class TestInstance(testtools.TestCase):

    @classmethod
    def setUpClass(self):     
        ctx = self.mock_ctx('init')
        
        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE ressource_group")
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
        network.create_network(ctx=ctx)
        #waiting for network class refacto 
        #current_ctx.set(ctx=ctx)
        #utils.wait_status(ctx, "network",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE subnet")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] = "10.0.1.0/24"
        network.create_subnet(ctx=ctx)
        #waiting for network class refacto 
        #current_ctx.set(ctx=ctx)
        #utils.wait_status(ctx, "network",constants.SUCCEEDED, 600)
      
        ctx.logger.info("CREATE public_ip")
        current_ctx.set(ctx=ctx)
        ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = "instancepublic_ip_test"
        public_ip.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE NIC")
        current_ctx.set(ctx=ctx)
        ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY] = "instancenic_test"
        ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = "instancepublic_ip_test"
        nic.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)
        
    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE nic")
        ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY] = "instancenic_test"
        nic.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE public_ip")
        ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = "instancepublic_ip_test"
        public_ip.delete(ctx=ctx)
        
        status_ip = constants.DELETING
        try:
            while status_ip == constants.DELETING :
                utils.wait_status(ctx, "public_ip","toto", 600)
                
        except utils.WindowsAzureError:
            pass

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE subnet")
        network.delete_subnet(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE network")
        network.delete_network(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE storage account")
        ctx.node.properties[constants.STORAGE_DELETABLE_KEY] = True
        storage.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE ressource_group")
        resource_group.delete(ctx=ctx)
 
    @classmethod 
    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
            constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
            constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
            constants.LOCATION_KEY: 'westeurope',
            constants.PUBLISHER_KEY: 'Canonical',
            constants.OFFER_KEY: 'UbuntuServer',
            constants.SKU_KEY: '12.04.5-LTS',
            constants.SKU_VERSION_KEY: 'latest',
            constants.FLAVOR_KEY: 'Standard_A1',
            constants.COMPUTE_KEY: test_name,
            constants.COMPUTE_USER_KEY: test_utils.COMPUTE_USER,
            constants.COMPUTE_PASSWORD_KEY: test_utils.COMPUTE_PASSWORD,
            constants.PUBLIC_KEY_KEY: test_utils.PUBLIC_KEY,
            constants.PRIVATE_KEY_KEY: test_utils.PRIVATE_KEY,
            constants.STORAGE_ACCOUNT_KEY: 'instancestraccounttest',
            constants.CREATE_OPTION_KEY:'FromImage',
            constants.RESOURCE_GROUP_KEY: 'instanceresource_group_test',
            constants.VIRTUAL_NETWORK_KEY: 'instancevirtual_network_test',
            constants.SUBNET_KEY: 'instancesubnet_test',
            'resources_prefix': 'instanceprefix',
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def setUp(self):
        super(TestInstance, self).setUp()


    def tearDown(self):
        super(TestInstance, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create(self):

        ctx = self.mock_ctx('testcreate')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(ctx.instance.id))
        ctx.logger.info("create VM") 

        instance.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create VM test")

    def test_delete(self):    
        ctx = self.mock_ctx('testdelete')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test")
    
        ctx.logger.info("create VM")    
        instance.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 600)
        
        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END delete VM test")

    def test_conflict(self):
        ctx = self.mock_ctx('testconflict')
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

    def test_concurrent_create(self):
        ctx1 = self.mock_ctx('testconcurrentcreate1')
        ctx2 = self.mock_ctx('testconcurrentcreate2')
        ctx1.logger.info("BEGIN concurrent create VM 1 test")
        ctx2.logger.info("BEGIN concurrent create VM 2 test")

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

        ctx1.logger.info("END concurrent create VM 1 test")
        ctx2.logger.info("END concurrent create VM 2 test")

    def test_concurrent_delete(self):
        ctx1 = self.mock_ctx('testconcurrentdelete1')
        ctx2 = self.mock_ctx('testconcurrentdelete2')

        ctx1.logger.info("BEGIN concurrent delete VM 1 test")
        ctx2.logger.info("BEGIN concurrent delete VM 2 test")

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

        ctx1.logger.info("END concurrent delete VM 1 test")
        ctx2.logger.info("END concurrent delete VM 2 test")


    def test_get_json(self):
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
    



