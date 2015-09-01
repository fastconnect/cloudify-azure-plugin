import testtools
import time
import test_utils

try:
    from plugin import utils
    from plugin import constants
    from plugin import nic
except:
    import utils
    import constants
    import nic

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestNIC(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': test_utils.SUBSCRIPTION_ID,
            'username': test_utils.AZURE_USERNAME, 
            'password': test_utils.AZURE_PASSWORD,
            'location': 'westeurope',
            'resource_group_name': 'resource_group_test',
            'management_network_name': 'management_network_test',
            'management_subnet_name': 'subnet_test',
        }

        test_runtime = {'public_ip_name': 'nic_test',
                        'network_interface_name': 'testnic'
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
        ctx.logger.info("BEGIN create NIC test:{}".format(ctx.instance.runtime_properties['public_ip_name']))

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
        ctx.logger.info("END create NIC  test")


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
        ctx.logger.info("END delete NIC  test")


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
