import testtools
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
            status_vm = instance.check_vm_status(ctx=ctx)
            time.sleep(20)     
        
        self.assertEqual( constants.SUCCEEDED, status_vm)
        instance.delete(ctx=ctx)


    def test_delete(self):
        ctx = self.mock_ctx('testdelete')
        current_ctx.set(ctx=ctx)

        instance.create(ctx=ctx) 

        current_ctx.set(ctx=ctx)
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            status_vm = instance.check_vm_status(ctx=ctx)
            time.sleep(20)
        
        instance.delete(ctx=ctx)

        time.sleep(20)
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
                          instance.check_vm_status,
                          ctx=ctx
                          )


'''
    def test_conflict(self):
        ctx = self.mock_ctx('testconflict')
        current_ctx.set(ctx=ctx)
        assertTrue(True)

    def test_stop(self):
        ctx = self.mock_ctx('teststop')
        current_ctx.set(ctx=ctx)
        assertTrue(True)
'''