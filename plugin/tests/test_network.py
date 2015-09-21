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

    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE network\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)


    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("DELETE network\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)
    

    @classmethod
    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY: 'networkresource_group_test'
            },
            constants.RESOURCE_GROUP_KEY: 'networkresource_group_test',
            constants.VIRTUAL_NETWORK_KEY: test_name,
            constants.VIRTUAL_NETWORK_ADDRESS_KEY: '10.0.0.0/16',
            constants.SUBNET_KEY: 'lan',
            constants.SUBNET_ADDRESS_KEY: '10.0.1.0/24',
            constants.DELETABLE_KEY: True
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
        ctx.logger.info("BEGIN test_create")

        self.assertEqual(201, network.create(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(202, network.delete(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_create")


    def test_delete_network(self):
        ctx = self.mock_ctx('testdeletenetwork')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_delete")

        status_code = network.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        self.assertEqual(202, network.delete(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")

        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_network = network.get_provisioning_state(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass
        
        ctx.logger.info("create network with deletable propertie set to false")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        status_code = network.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)
          

        ctx.logger.info("not delete network")
        self.assertEqual(0, network.delete(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True

        ctx.logger.info("delete network")
        self.assertEqual(202, network.delete(ctx=ctx))

        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_network = network.get_provisioning_state(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_delete")


    def test_conflict_network(self):
        ctx = self.mock_ctx('testconflictnetwork')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_network")

        self.assertEqual(201, network.create(ctx=ctx))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        ctx.logger.info("Conflict Creating Virtual Network")
        self.assertNotEqual(201, network.create(ctx=ctx))
        ctx.logger.info("Conflict detected")

        self.assertEqual(202, network.delete(ctx=ctx))

        ctx.logger.info("Checking Virtual Network deleted")

        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_network = network.get_provisioning_state(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("check is Virtual Network is release")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_conflict_network")