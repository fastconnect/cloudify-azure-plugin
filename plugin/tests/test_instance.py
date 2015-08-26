﻿import testtools
import time
import test_utils
import inspect

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import instance

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
            'network_interface_name': 'fcnic',
            'storage_account': 'fastconnectstorage',
            'create_option':'FromImage',
            'resource_group_name': 'FCtest',
            'management_network_name': 'fcvnet',
            'management_subnet_name': 'subnet',
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
            status_vm = instance.get_vm_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)    
        
        ctx.logger.info("check VM creation success")
        self.assertEqual(constants.SUCCEEDED, status_vm)

        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("check if NIC is release")
        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None :
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(ctx=ctx)
            time.sleep(TIME_DELAY)
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
            status_vm = instance.get_vm_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check VM creation success")
        self.assertEqual( constants.SUCCEEDED, status_vm)
        
        ctx.logger.info("delete VM")
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("check if NIC is release")
        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(
                                    ctx=ctx
                                )

            time.sleep(TIME_DELAY)
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
            status_vm = instance.get_vm_provisioning_state(
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

        ctx.logger.info("check if NIC is release")
        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(
                                ctx=ctx
                            )
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check vm provisionning state in a deleted machine")
        self.assertRaises(
                          utils.WindowsAzureError,
                          instance.get_vm_provisioning_state,
                          ctx=ctx
                          )

        ctx.logger.info("delete VM conflict")
        self.assertEqual(204, instance.delete(ctx=ctx))
        ctx.logger.info("END conflict VM test")
        time.sleep(TIME_DELAY)
     
    def test_stop(self):
        ctx = self.mock_ctx('teststop')
        current_ctx.set(ctx=ctx)

