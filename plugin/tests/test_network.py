import testtools
import time
import test_utils
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    network
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError
TIME_DELAY = 20

class TestNetwork(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))

    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test network number " + self.__random_id)
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
                constants.RESOURCE_GROUP_KEY:\
                    'networkresource_group_test' + self.__random_id
            },
            constants.RESOURCE_GROUP_KEY:\
                'networkresource_group_test' + self.__random_id,
            constants.VIRTUAL_NETWORK_KEY: test_name + self.__random_id,
            constants.VIRTUAL_NETWORK_ADDRESS_KEY: '10.0.0.0/16',
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

        status_code = network.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network",constants.SUCCEEDED, timeout=600) 

        self.assertEqual(202, network.delete(ctx=ctx))
        ctx.logger.info("Checking Virtual Network deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            utils.wait_status,
            ctx,
            'network'
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_create")


    def test_delete_network(self):
        ctx = self.mock_ctx('testdeletenetwork')
        current_ctx.set(ctx=ctx)

        ctx.logger.info("BEGIN test_delete")
        ctx.logger.info("create network with deletable propertie set to false")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        status_code = network.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network",constants.SUCCEEDED, timeout=600)

        ctx.logger.info("not delete network")
        self.assertEqual(0, network.delete(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True

        ctx.logger.info("delete network")
        self.assertEqual(202, network.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "network", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_delete")


    def test_conflict_network(self):
        ctx = self.mock_ctx('testconflictnetwork')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_network")

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        self.assertEqual(201, network.create(ctx=ctx))
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network", constants.SUCCEEDED, timeout=600)

        ctx.logger.info("Conflict Creating Virtual Network")
        current_ctx.set(ctx=ctx)
        self.assertNotEqual(201, network.create(ctx=ctx))
        ctx.logger.info("Conflict detected")

        current_ctx.set(ctx=ctx)
        self.assertEqual(202, network.delete(ctx=ctx))
        ctx.logger.info("Checking Virtual Network deleted")

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "network", "waiting for exception", timeout=600)
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

    def test_conflict_network_address(self):
        ctx = self.mock_ctx('testconflictnetworkaddress')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_network_address")

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        self.assertEqual(201, network.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network", constants.SUCCEEDED, timeout=600)

        ctx.logger.info("Conflict Creating Virtual Network")
        ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY] = '10.9.0.0/16'
        current_ctx.set(ctx=ctx)
        self.assertRaises(NonRecoverableError, network.create, ctx=ctx)
        ctx.logger.info("Conflict detected")

        current_ctx.set(ctx=ctx)
        self.assertEqual(202, network.delete(ctx=ctx))
        ctx.logger.info("Checking Virtual Network deleted")

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "network", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("check is Virtual Network is release")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_conflict_network_address")