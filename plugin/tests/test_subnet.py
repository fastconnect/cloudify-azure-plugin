import testtools
import time
import test_utils
import test_mockcontext

from plugin import (utils,
                    constants,
                    resource_group,
                    subnet,
                    network
                    )

from cloudify.state import current_ctx

TIME_DELAY = 20

class TestSubnet(testtools.TestCase):

    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE subnet\'s required resources")
        
        ctx.logger.info("CREATE resource_group")        
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[
            constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create(ctx=ctx)

    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        ctx.logger.info("DELETE subnet\'s required resources")

        ctx.logger.info("DELETE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[
            constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create(ctx=ctx)
        
        ctx.logger.info("DELETE resource_group")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)

    @classmethod
    def mock_ctx(self, test_name, cdir='10.0.1.0/24'):
        """ Creates a mock context for the instance
            tests
        """
        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY: 'subnetresource_group_test'
            },
            constants.RESOURCE_GROUP_KEY: 'subnetresource_group_test',
            constants.SUBNET_KEY: test_name,
            constants.SUBNET_ADDRESS_KEY: cdir,
            constants.VIRTUAL_NETWORK_KEY: 'subnetnetwork_test',
            constants.DELETABLE_KEY: True
        }

        test_runtime = {
            constants.VIRTUAL_NETWORK_KEY: 'subnetnetwork_test'
        }

        test_relationships = [ 
                                {
                                'node_id': 'test',
                                'relationship_type':\
                                    constants.SUBNET_CONNECTED_TO_NETWORK,
                                'relationship_properties': \
                                    {constants.VIRTUAL_NETWORK_KEY: \
                                                    'subnetnetwork_test'}
                                }
                             ]

        return test_mockcontext.MockCloudifyContextRelationships(
                                node_id='test',
                                properties=test_properties,
                                runtime_properties=test_runtime,
                                relationships=test_relationships
                                )


    def setUp(self):
        super(TestSubnet, self).setUp()

    def tearDown(self):
        super(TestSubnet, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create_subnet(self):
        ctx = self.mock_ctx('testcreatesubnet', cdir='10.0.2.0/24')
        ctx.logger.info("BEGIN test_create_subnet")

        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = subnet.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)




        status_subnet = constants.DELETING
        try:
            while status_subnet == constants.DELETING :
                current_ctx.set(ctx=ctx)           
                status_subnet = subnet.get_provisioning_state(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_create_subnet")

    def test_delete_subnet(self):
        ctx = self.mock_ctx('testdeletesubnet', cdir='10.0.3.0/24')
        ctx.logger.info("BEGIN test_delete_subnet")
        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = subnet.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)

        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        ctx.logger.info("Checking Subnet deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            subnet.get_provisioning_state,
            ctx=ctx
        )

        ctx.logger.info("create subnet with deletable propertie set to false")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = subnet.get_provisioning_state(ctx=ctx)
            ctx.logger.info("subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)
          
        ctx.logger.info("not delete subnet")
        self.assertEqual(0, subnet.delete(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True

        ctx.logger.info("delete subnet")
        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        status_subnet = constants.DELETING
        try:
            while status_subnet == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_subnet = subnet.get_provisioning_state(ctx=ctx)
                ctx.logger.info("subnet status is " + status_subnet)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_delete_subnet")

    def test_conflict_subnet(self):
        ctx = self.mock_ctx('testconflictsubnet', cdir='10.0.4.0/24')
        ctx.logger.info("BEGIN test_conflict_subnet")

        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_subnet = constants.CREATING
        while status_subnet != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_subnet = subnet.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Subnet status is " + status_subnet)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Subnet Created")
        self.assertEqual(constants.SUCCEEDED, status_subnet)

        ctx.logger.info("Conflict Creating Subnet")
        self.assertNotEqual(201, subnet.create(ctx=ctx))
        ctx.logger.info("Conflict detected")

        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        status_subnet = constants.DELETING
        try:
            while status_subnet == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_subnet = subnet.get_provisioning_state(ctx=ctx)
                ctx.logger.info("Virtual subnet status is " + status_subnet)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("Checking Subnet deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            subnet.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Subnet Deleted")

        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        status_subnet = constants.DELETING
        try:
            while status_subnet == constants.DELETING :
                current_ctx.set(ctx=ctx)
                status_subnet = subnet.get_provisioning_state(ctx=ctx)
                ctx.logger.info("Virtual subnet status is " + status_subnet)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("check is Virtual subnet is release")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            subnet.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Virtual subnet Deleted")
        ctx.logger.info("END test_conflict_subnet")