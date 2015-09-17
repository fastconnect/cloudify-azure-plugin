import testtools
import time
import test_utils

from plugin import (utils,
                    constants,
                    resource_group,
                    public_ip
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestPublicIP(testtools.TestCase):
    
    @classmethod
    def setUpClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE public_ip\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)


    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        ctx.logger.info("DELETE public_ip\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)

    
    @classmethod
    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """
        test_properties = {
            constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
            constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
            constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
            constants.LOCATION_KEY: 'westeurope',
            constants.RESOURCE_GROUP_KEY: 'publicipresource_group_test',
        }

        test_runtime = {
            constants.PUBLIC_IP_KEY: test_name,
        }

        return MockCloudifyContext(node_id='test',
            properties=test_properties,
            runtime_properties=test_runtime,
        )


    def setUp(self):
        super(TestPublicIP, self).setUp()


    def tearDown(self):
        super(TestPublicIP, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_public_ip(self):
        ctx = self.mock_ctx('testcreateip')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create public_ip test")

        ctx.logger.info("create public_ip")
        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, 600)    

        ctx.logger.info("delete public_ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))

        status_ip = constants.DELETING
        try:
            while status_ip == constants.DELETING :
                current_ctx.set(ctx=ctx)
                utils.wait_status(ctx, "public_ip","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END create public_ip test")


    def test_delete_public_ip(self):
        ctx = self.mock_ctx('testdeleteip')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN public_ip delete test")

        ctx.logger.info("create public_ip")   
        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, 600)

        ctx.logger.info("delete public_ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))
        
        status_ip = constants.DELETING
        try:
            while status_ip == constants.DELETING :
                current_ctx.set(ctx=ctx)
                utils.wait_status(ctx, "public_ip","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END public_ip delete test")


    def test_conflict_public_ip(self):
        ctx = self.mock_ctx('testconflictip')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict public_ip test")

        ctx.logger.info("create public_ip")
        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, 600)

        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        ctx.logger.info("delete public_ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))

        status_ip = constants.DELETING
        try:
            while status_ip == constants.DELETING :
                current_ctx.set(ctx=ctx)
                utils.wait_status(ctx, "public_ip","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("delete conflict public_ip")
        self.assertEqual(204, public_ip.delete(ctx=ctx))
        
        ctx.logger.info("END conflict public_ip test")