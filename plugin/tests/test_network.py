﻿import testtools
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

        status_code = network.create_network(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)

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

        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_network = network.get_provisioning_state_network(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass
        
        ctx.logger.info("create network with deletable propertie set to false")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        status_code = network.create_network(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)
          

        ctx.logger.info("not delete network")
        self.assertEqual(0, network.delete_network(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True

        ctx.logger.info("delete network")
        self.assertEqual(202, network.delete_network(ctx=ctx))

        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_network = network.get_provisioning_state_network(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

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

        ctx.logger.info("Checking Virtual Network deleted")

        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_network = network.get_provisioning_state_network(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

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
        ctx.logger.info("BEGIN test_create_subnet")
        current_ctx.set(ctx=ctx)
        status_code = network.create_network(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        current_ctx.set(ctx=ctx)
        status_code = network.create_subnet(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)

        self.assertEqual(202, network.delete_network(ctx=ctx))
        status_network = constants.DELETING
        try:
            while status_network == constants.DELETING :
                current_ctx.set(ctx=ctx)           
                status_network = network.get_provisioning_state_network(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_create_subnet")


    def test_delete_subnet(self):
        ctx = self.mock_ctx('testdeletesubnet')
        ctx.node.properties[constants.VIRTUAL_NETWORK_KEY] = 'testsubnetnetwork'
        ctx.node.properties[constants.SUBNET_KEY] = 'testdeletesubnet'
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_delete_subnet")
        status_code = network.create_network(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)

        status_code = network.create_subnet(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

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

        ctx.logger.info("create subnet with deletable propertie set to false")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        current_ctx.set(ctx=ctx)
        status_code = network.create_subnet(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))


        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
            ctx.logger.info("subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)
          

        ctx.logger.info("not delete subnet")
        self.assertEqual(0, network.delete_subnet(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True

        ctx.logger.info("delete subnet")
        self.assertEqual(202, network.delete_subnet(ctx=ctx))

        status_subnet = constants.DELETING
        try:
            while status_subnet == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_subnet)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_delete_subnet")


    def test_conflict_subnet(self):
        ctx = self.mock_ctx('testconflictsubnet')
        ctx.node.properties[constants.VIRTUAL_NETWORK_KEY] = 'testsubnetnetwork'
        ctx.node.properties[constants.SUBNET_KEY] = 'testconflictsubnet'
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_subnet")
        status_code = network.create_network(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))


        status_network = constants.CREATING
        while status_network != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_network = network.get_provisioning_state_network(ctx=ctx)
            ctx.logger.info("Virtual Network status is " + status_network)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Virtual Network Created")
        self.assertEqual(constants.SUCCEEDED, status_network)
        status_code = network.create_subnet(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))


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

        status_subnet = constants.DELETING
        try:
            while status_subnet == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_subnet = network.get_provisioning_state_subnet(ctx=ctx)
                ctx.logger.info("Virtual Network status is " + status_subnet)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

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
                ctx.logger.info("Virtual Network status is " + status_network)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("check is Virtual Network is release")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            network.get_provisioning_state_network,
            ctx=ctx
        )
        ctx.logger.info("Virtual Network Deleted")
        ctx.logger.info("END test_conflict_subnet")
