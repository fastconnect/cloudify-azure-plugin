﻿import testtools
import time
import test_utils

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import instance

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

TIME_DELAY = 30

class TestInstance(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': SUBSCRIPTION_ID,
            'username': AZURE_USERNAME, 
            'password': AZURE_PASSWORD,
            'location': 'westeurope',
            'publisherName': 'Canonical',
            'offer': 'UbuntuServer',
            'sku': '12.04.5-LTS',
            'version': 'latest',
            'flavor_id': 'Standard_A1',
            'compute_name': test_name,
            'compute_user': COMPUTE_USER,
            'compute_password': COMPUTE_PASSWORD,
            'resources_prefix': 'boulay',
            'network_interface_name': 'cloudifynic',
            'storage_account': 'cloudifystorageaccount',
            'create_option':'FromImage',
            'resource_group_name': 'cloudifygroup',
            'management_network_name': 'cloudifynetwork',
            'management_subnet_name': 'cloudifysubnet'
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)


    def setUp(self):
        super(TestInstance, self).setUp()


    def tearDown(self):
        super(TestInstance, self).tearDown()
        time.sleep(30)


    def test_create(self):
        ctx = self.mock_ctx('testcreate')
        
        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx) 

        current_ctx.set(ctx=ctx)
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            status_vm = instance.get_vm_provisioning_state(ctx=ctx)
            time.sleep(20)     
        
        current_ctx.set(ctx=ctx)
        self.assertEqual( constants.SUCCEEDED, status_vm)
        
        current_ctx.set(ctx=ctx)
        instance.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        nic_machine_id = "nicmachineName"
        while nic_machine_id != "":
            nic_machine_id = instance.get_nic_virtual_machine_id(ctx=ctx)
            time.sleep(20)
'''
   
    def test_delete(self):
        ctx = self.mock_ctx('testdelete')
 
        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx) 

        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_vm_provisioning_state(ctx=ctx)
            time.sleep(20)
        
        current_ctx.set(ctx=ctx)
        instance.delete(ctx=ctx)

        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(ctx=ctx)
            time.sleep(20)
    
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
                          instance.get_vm_provisioning_state,
                          ctx=ctx
                          )

    def test_conflict(self):
        ctx = self.mock_ctx('testconflict')

        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx)
        
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_vm_status(ctx=ctx)
            time.sleep(20)

        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
                         instance.create,
                         ctx=ctx
                         )

        current_ctx.set(ctx=ctx)
        instance.delete(ctx=ctx)

        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(ctx=ctx)
            time.sleep(20)

        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
                          instance.get_vm_status,
                          ctx=ctx
                          )

        current_ctx.set(ctx=ctx) 
        self.assertRaises(utils.WindowsAzureError,
                          instance.delete,
                          ctx=ctx
                          )

    def test_stop(self):
        ctx = self.mock_ctx('teststop')
        current_ctx.set(ctx=ctx)
        assertTrue(True)
'''