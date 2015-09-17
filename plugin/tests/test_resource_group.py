import testtools
import time
import test_utils

from plugin import (utils,
                    constants,
                    resource_group
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestResourceGroup(testtools.TestCase):

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
                constants.RESOURCE_GROUP_KEY: test_name
            },
            constants.RESOURCE_GROUP_KEY: test_name
        }

        return MockCloudifyContext(node_id = 'test',
                                   properties = test_properties)

    def setUp(self):
        super(TestResourceGroup, self).setUp()


    def tearDown(self):
        super(TestResourceGroup, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create_resource_group(self):
        ctx = self.mock_ctx('testcreategroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN resource_group create test")

        ctx.logger.info("create resource_group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, 600)  

        ctx.logger.info("delete resource_group")
        self.assertEqual(202, resource_group.delete(ctx=ctx))

        status_resource_group = constants.DELETING
        try:
            while status_resource_group == constants.DELETING :
                current_ctx.set(ctx=ctx)
                utils.wait_status(ctx, "resource_group","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END resource_group create test")


    def test_delete_resource_group(self):
        ctx = self.mock_ctx('testdeletegroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN resource_group delete test")

        ctx.logger.info("create resource_group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, 600)      

        ctx.logger.info("delete resource_group")
        self.assertEqual(202, resource_group.delete(ctx=ctx))

        status_resource_group = constants.DELETING
        try:
            while status_resource_group == constants.DELETING :
                current_ctx.set(ctx=ctx)
                utils.wait_status(ctx, "resource_group","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END resource_group delete test")


    def test_conflict_resource_group(self):
        ctx = self.mock_ctx('conflictgroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN resource_group conflict test")

        ctx.logger.info("create resource group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, 600)    

        ctx.logger.info("conflict create resource group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        ctx.logger.info("delete resource_group")
        self.assertEqual(202, resource_group.delete(ctx=ctx))
        
        status_resource_group = constants.DELETING
        try:
            while status_resource_group == constants.DELETING :
                current_ctx.set(ctx=ctx)
                utils.wait_status(ctx, "resource_group","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END resource_group conflict test")