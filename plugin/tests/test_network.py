import testtools
import time
import test_utils

from plugin import utils
from plugin import constants
from plugin import network

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestNetwork(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': test_utils.SUBSCRIPTION_ID,
            'username': test_utils.AZURE_USERNAME,
            'password': test_utils.AZURE_PASSWORD,
            'location': 'westeurope',
            'resource_group_name': 'cloudifygroup',
            'virtual_network_name': test_name,
            'virtual_network_address_prefix': '10.0.0.0/16',
            'subnet_name': 'lan',
            'subnet_address_prefix': '10.0.1.0/24'
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def setUp(self):
        super(TestNetwork, self).setUp()


    def tearDown(self):
        super(TestNetwork, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_network(self):
        ctx = self.mock_ctx('testcreatenetwork')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_create_network")

        self.assertEqual(201, network.create_network(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_create_network")
        #self.assertTrue(False)


    def test_delete_network(self):
        ctx = self.mock_ctx('testdeletenetwork')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_delete_network")

        self.assertEqual(201, network.create_network(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_delete_network")
        #self.assertTrue(False)


    def test_conflict_network(self):
        ctx = self.mock_ctx('testconflictnetwork')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_network")

        self.assertEqual(201, network.create_network(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        ctx.logger.info("Conflict Creating Virtual Network")
        self.assertNotEqual(201, network.create_network(ctx=ctx))
        ctx.logger.info("Conflict detected")

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("check is Virtual Network is release")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")

        ctx.logger.info("END test_conflict_network")
        #self.assertTrue(False)


    def test_create_subnet(self):
        ctx = self.mock_ctx('testcreatesubnet')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_create_subnet")

        self.assertEqual(201, network.create_network(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(201, network.create_subnet(ctx=ctx))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)

        self.assertEqual(202, network.delete_subnet(ctx=ctx))

        ctx.logger.info("Checking Subnet deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_subnet,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_create_subnet")
        #self.assertTrue(False)


    def test_delete_subnet(self):
        ctx = self.mock_ctx('testdeletesubnet')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_delete_subnet")

        self.assertEqual(201, network.create_network(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(201, network.create_subnet(ctx=ctx))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)

        self.assertEqual(202, network.delete_subnet(ctx=ctx))

        ctx.logger.info("Checking Subnet deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_subnet,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_delete_subnet")
        #self.assertTrue(False)


    def test_conflict_subnet(self):
        ctx = self.mock_ctx('testconflictsubnet')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_subnet")

        self.assertEqual(201, network.create_network(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(201, network.create_subnet(ctx=ctx))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)

        ctx.logger.info("Conflict Creating Subnet")
        self.assertNotEqual(201, network.create_subnet(ctx=ctx))
        ctx.logger.info("Conflict detected")

        self.assertEqual(202, network.delete_subnet(ctx=ctx))

        ctx.logger.info("Checking Subnet deleted")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_subnet,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("check is Virtual Network is release")
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")

        ctx.logger.info("END test_conflict_subnet")
        #self.assertTrue(False)