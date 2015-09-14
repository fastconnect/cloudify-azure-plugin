import testtools
import time
import test_utils

from plugin import (utils,
                    constants,
                    resource_group,
                    network
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestNetwork(testtools.TestCase):

    def __init__(self, *args):
        super(TestNetwork, self).__init__(*args)

        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE network\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
            constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
            constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
            constants.LOCATION_KEY: 'westeurope',
            constants.RESOURCE_GROUP_KEY: 'resource_group_test',
            constants.VIRTUAL_NETWORK_KEY: test_name,
            constants.VIRTUAL_NETWORK_ADDRESS_KEY: '10.0.0.0/16',
            constants.SUBNET_KEY: 'lan',
            constants.SUBNET_ADDRESS_KEY: '10.0.1.0/24'
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
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_create_network")


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
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_delete_network")


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
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_conflict_network")


    def test_create_subnet(self):
        ctx = self.mock_ctx('testcreatesubnet')
        ctx.node.properties[constants.VIRTUAL_NETWORK_KEY] = 'testsubnetnetwork'
        ctx.node.properties[constants.SUBNET_KEY] = 'testcreatesubnet'
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
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_subnet,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        self.assertEqual(202, network.delete_network(ctx=ctx))
        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)           
                status_network = network.get_provisioning_state_network(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_create_subnet")


    def test_delete_subnet(self):
        ctx = self.mock_ctx('testdeletesubnet')
        ctx.node.properties[constants.VIRTUAL_NETWORK_KEY] = 'testsubnetnetwork'
        ctx.node.properties[constants.SUBNET_KEY] = 'testdeletesubnet'
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
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_subnet,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_delete_subnet")


    def test_conflict_subnet(self):
        ctx = self.mock_ctx('testconflictsubnet')
        ctx.node.properties[constants.VIRTUAL_NETWORK_KEY] = 'testsubnetnetwork'
        ctx.node.properties[constants.SUBNET_KEY] = 'testconflictsubnet'
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
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_subnet,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        self.assertEqual(202, network.delete_network(ctx=ctx))

        ctx.logger.info("check is Virtual Network is release")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_conflict_subnet")

    def __del__(self, *args):
        super(TestStorage, self).__init__(*args)

        ctx = self.mock_ctx('init')
        ctx.logger.info("DELETE network\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)