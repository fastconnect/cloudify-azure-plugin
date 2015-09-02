import testtools
import time
import test_utils
import inspect
import threading
import Queue

from plugin import (utils,
                    constants,
                    instance
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

TIME_DELAY = 20

class TestInstance(testtools.TestCase):
    
    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': test_utils.SUBSCRIPTION_ID,
            'username': test_utils.AZURE_USERNAME, 
            'password': test_utils.AZURE_PASSWORD,
            'location': 'westeurope',
            'publisherName': 'Canonical',
            'offer': 'UbuntuServer',
            'sku': '12.04.5-LTS',
            'version': 'latest',
            'flavor_id': 'Standard_A1',
            'compute_name': test_name,
            'compute_user': test_utils.COMPUTE_USER,
            'compute_password': test_utils.COMPUTE_PASSWORD,
            'public_key': test_utils.PUBLIC_KEY,
            'private_key': test_utils.PRIVATE_KEY,
            'resources_prefix': 'boulay',
            #'network_interface_name': '', #TODO: auto-generated nic per instance
            'storage_account': 'storageaccounttest3',
            'create_option':'FromImage',
            'resource_group_name': 'resource_group_test',
            'management_network_name': 'management_network_test',
            'management_subnet_name': 'subnet_test',
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
        
        ctx.logger.info("check VM status")
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)    
        
        ctx.logger.info("check VM creation success")
        self.assertEqual(constants.SUCCEEDED, status_vm)

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END create VM test")

    def test_delete(self):    
        ctx = self.mock_ctx('testdelete')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test")
    
        ctx.logger.info("create VM")    
        instance.create(ctx=ctx) 

        ctx.logger.info("check VM status")
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check VM creation success")
        self.assertEqual( constants.SUCCEEDED, status_vm)
        
        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("END delete VM test")

    def test_conflict(self):
        ctx = self.mock_ctx('testconflict')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict VM test")

        ctx.logger.info("create VM")
        instance.create(ctx=ctx)
        
        ctx.logger.info("check VM creation success")
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_provisioning_state(
                            ctx=ctx
                        )
            time.sleep(TIME_DELAY)

        ctx.logger.info("VM creation conflict")
        self.assertRaises(utils.WindowsAzureError,
                         instance.create,
                         ctx=ctx
                         )

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

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
        #current_ctx.set(ctx=ctx)
        ctx1.logger.info("BEGIN concurrent create VM 1 test")
        ctx2.logger.info("BEGIN concurrent create VM 2 test")

        def create_vm(lctx):
            instance.create(ctx=lctx)
            return
        vm1 = threading.Thread(target=create_vm, args=(ctx1,))
        vm2 = threading.Thread(target=create_vm, args=(ctx2,))

        ctx1.logger.info("create VM 1")
        #instance.create(ctx=ctx1)
        vm1.start()

        ctx2.logger.info("create VM 2")
        #instance.create(ctx=ctx2)
        vm2.start()

        vm1.join()
        vm2.join()

        ctx1.logger.info("check VM 1 status")
        ctx2.logger.info("check VM 2 status")
        status_vm1 = constants.CREATING
        status_vm2 = constants.CREATING
        while bool(status_vm1 == constants.CREATING or status_vm2 == constants.CREATING) :
            #current_ctx.set(ctx=ctx)
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
        #current_ctx.set(ctx=ctx)
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
            #current_ctx.set(ctx=ctx)
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
        #self.assertEqual(202, instance.delete(ctx=ctx1))
        vm1.start()

        ctx2.logger.info("delete VM 2")
        #self.assertEqual(202, instance.delete(ctx=ctx2))
        vm2.start()

        vm1.join()
        vm2.join()
        
        self.assertEqual(202, queue1.get())
        self.assertEqual(202, queue2.get())

        ctx1.logger.info("END concurrent delete VM 1 test")
        ctx2.logger.info("END concurrent delete VM 2 test")
