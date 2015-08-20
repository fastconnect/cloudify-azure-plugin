import testtools
import time
import test_utils

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import public_ip

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestPublicIP(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': test_utils.SUBSCRIPTION_ID,
            'username': test_utils.AZURE_USERNAME, 
            'password': test_utils.AZURE_PASSWORD,
            'location': 'westeurope',
            'network_interface_name': 'testnic',
            'resource_group_name': 'cloudifygroup',
            'public_ip_name': 'testpublicip',
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def setUp(self):
        super(TestPublicIP, self).setUp()


    def tearDown(self):
        super(TestPublicIP, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_public_ip(self):
        ctx = self.mock_ctx('testcreatenic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create public_ip test")

        ctx.logger.info("create public_ip")
        public_ip.create(ctx=ctx)

        status_ip = constants.CREATING
        while status_ip == constants.CREATING :
            current_ctx.set(ctx=ctx)
            ctx.logger.debug(status_ip)
            status_ip = public_ip.get_public_ip_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.debug(status_ip)
        ctx.logger.info("check public_ip creation success")
        self.assertEqual( constants.SUCCEEDED, status_ip)

        ctx.logger.info("delete public_ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))
        ctx.logger.info("END create public_ip  test")


    #def test_delete_public_ip(self):

