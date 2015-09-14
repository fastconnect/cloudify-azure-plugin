import testtools
import time
import test_utils

from plugin import (utils,
                    constants,
                    resource_group,
                    public_ip,
                    network,
                    nic
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20


class TestNIC(testtools.TestCase):
    def __init__(self, *args):
        super(TestNIC, self).__init__(*args)

        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE NIC\'s required resources")

        ctx.logger.info("CREATE ressource_group")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

        ctx.logger.info("CREATE public_ip")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.PUBLIC_IP_KEY] = "public_ip_test"
        public_ip.create(ctx=ctx)
        
        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create_network(ctx=ctx)

        ctx.logger.info("CREATE subnet")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] = "10.0.1.0/24"
        network.create_subnet(ctx=ctx)


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
            constants.VIRTUAL_NETWORK_KEY: 'management_network_test',
            constants.SUBNET_KEY: 'subnet_test',
        }

        test_runtime = {
            'public_ip_name': 'nic_test',
            'network_interface_name': test_name,
        }

        return MockCloudifyContext(node_id='test',
            properties=test_properties,
            runtime_properties=test_runtime
        )

    def setUp(self):
        super(TestNIC, self).setUp()


    def tearDown(self):
        super(TestNIC, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create(self):
        ctx = self.mock_ctx('testcreatenic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create NIC test")

        ctx.logger.info("create NIC")
        nic.create(ctx=ctx)

        status_nic = constants.CREATING
        while status_nic == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_nic = nic.get_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check NIC creation success")
        self.assertEqual( constants.SUCCEEDED, status_nic)

        ctx.logger.info("delete NIC")
        self.assertEqual(202, nic.delete(ctx=ctx))

        ctx.logger.info("check is NIC is release")
        self.assertRaises(utils.WindowsAzureError,
                         nic.get_provisioning_state,
                         ctx=ctx
                         )
        
        ctx.logger.info("END create NIC test")


    def test_delete(self):
        ctx = self.mock_ctx('testdeletenic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete NIC test")

        ctx.logger.info("create NIC")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_nic = constants.CREATING
        while status_nic == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_nic = nic.get_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check NIC creation success")
        self.assertEqual( constants.SUCCEEDED, status_nic)

        ctx.logger.info("delete NIC")
        self.assertEqual(202, nic.delete(ctx=ctx))

        ctx.logger.info("check is NIC is release")
        self.assertRaises(utils.WindowsAzureError,
                         nic.get_provisioning_state,
                         ctx=ctx
                         )

        ctx.logger.info("END delete NIC test")


    def test_conflict(self):
        ctx = self.mock_ctx('testconflictnic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict NIC test")

        ctx.logger.info("create NIC")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_nic = constants.CREATING
        while status_nic == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_nic = nic.get_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check NIC creation success")
        self.assertEqual( constants.SUCCEEDED, status_nic)

        ctx.logger.info("create NIC conflict")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        ctx.logger.info("delete NIC")
        self.assertEqual(202, nic.delete(ctx=ctx))

        ctx.logger.info("check is NIC is release")
        self.assertRaises(utils.WindowsAzureError,
                         nic.get_provisioning_state,
                         ctx=ctx
                         )

        ctx.logger.info("delete NIC conflict")
        self.assertEqual(204, nic.delete(ctx=ctx))

        ctx.logger.info("END create NIC  test")


    def __del__(self):
        super(TestNIC, self).__init__(*args)

        ctx = self.mock_ctx('init')
        ctx.logger.info("DELETE public_ip\'s required resources")

        ctx.logger.info("DELETE ressource group")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)

        ctx.logger.info("DELETE network")
        current_ctx.set(ctx=ctx)
        network.delete_network(ctx=ctx)
        
        ctx.logger.info("DELETE subnet")
        current_ctx.set(ctx=ctx)
        network.delete_subnet(ctx=ctx)