import testtools
import time
import test_utils
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    availability_set
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestAvailabilitySet(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))

    @classmethod
    def setUpClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test availability_set number " + self.__random_id)
        ctx.logger.info("CREATE availability set required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        ctx.logger.info("DELETE availability set required resources")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)


    @classmethod
    def mock_ctx(self, test_name):
        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY:\
                    'avail_set_res_group_test' + self.__random_id,
            },
            constants.RESOURCE_GROUP_KEY:\
                'avail_set_res_group_test' + self.__random_id,
            constants.AVAILABILITY_SET_KEY: test_name + self.__random_id,
            constants.DELETABLE_KEY: True
        }
        #should not be empty
        test_runtime = {
            'not': 'empty'
        }

        return MockCloudifyContext(node_id='test',
            properties=test_properties,
            runtime_properties=test_runtime,
        )


    def setUp(self):
        super(TestAvailabilitySet, self).setUp()


    def tearDown(self):
        super(TestAvailabilitySet, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_availability_set(self):
        ctx = self.mock_ctx('testcreateavailabilityset')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create availability_set test")

        ctx.logger.info("create availability_set")
        self.assertEqual(200, availability_set.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "availability_set",constants.SUCCEEDED, 600)

        ctx.logger.info("delete availability_set")
        self.assertEqual(200, availability_set.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "availability_set","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END create availability_set test")


    def test_delete_availability_set(self):
        ctx = self.mock_ctx('testdeleteavailabilityset')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete availability_set test")

        ctx.logger.info("create availability_set")
        self.assertEqual(200, availability_set.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "availability_set",constants.SUCCEEDED, 600)

        ctx.logger.info("trying to delete an non-deletable availability_set")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        current_ctx.set(ctx=ctx)
        self.assertEqual(0, availability_set.delete(ctx=ctx))

        ctx.logger.info("delete availability_set")
        ctx.node.properties[constants.DELETABLE_KEY] = True
        current_ctx.set(ctx=ctx)
        self.assertEqual(200, availability_set.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "availability_set","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END delete availability_set test")


    def test_conflict_availability_set(self):
        ctx = self.mock_ctx('testconflictavailabilityset')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict availability_set test")

        ctx.logger.info("create availability_set")
        self.assertEqual(200, availability_set.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "availability_set",constants.SUCCEEDED, 600)

        ctx.logger.info("create conflict availability_set")
        self.assertEqual(200, availability_set.create(ctx=ctx))

        ctx.logger.info("delete availability_set")
        self.assertEqual(200, availability_set.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "availability_set","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("delete conflict availability_set")
        self.assertEqual(204, availability_set.delete(ctx=ctx))

        ctx.logger.info("END conflict availability_set test")