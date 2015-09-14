import testtools
import time
import test_utils

from plugin import (utils,
                    constants,
                    resource_group,
                    storage,
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestStorage(testtools.TestCase):

    def __init__(self, *args):
        super(TestStorage, self).__init__(*args)

        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE storage_account\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

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
            constants.STORAGE_ACCOUNT_KEY: test_name,
            constants.ACCOUNT_TYPE_KEY: 'Standard_LRS', #Standard_LRS|Standard_ZRS|Standard_GRS|Standard_RAGRS|Premium_LRS
            constants.STORAGE_DELETABLE_KEY: True
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def setUp(self):
        super(TestStorage, self).setUp()


    def tearDown(self):
        super(TestStorage, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_storage(self):
        ctx = self.mock_ctx('testcreatestorage')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test create storage")

        status_code = storage.create(ctx=ctx)
        ctx.logger.info("status_code : " + str(status_code))
        self.assertTrue(bool((status_code == 200) | (status_code == 202)))

        status_storage = constants.CREATING
        while status_storage != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_storage = storage.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Storage Account status is " + status_storage)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Storage Account Created")
        self.assertEqual(constants.SUCCEEDED, status_storage)

        self.assertEqual(200, storage.delete(ctx=ctx))

        ctx.logger.info("Checking Storage Account deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")

        ctx.logger.info("END test create storage")
 

    def test_delete_storage(self):
        ctx = self.mock_ctx('testdeletestorage')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test delete storage")

        status_code = storage.create(ctx=ctx)
        ctx.logger.info("status_code : " + str(status_code))
        self.assertTrue(bool((status_code == 200) | (status_code == 202)))

        status_storage = constants.CREATING
        while status_storage != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_storage = storage.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Storage Account status is " + status_storage)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Storage Account Created")
        self.assertEqual(constants.SUCCEEDED, status_storage)

        self.assertEqual(200, storage.delete(ctx=ctx))

        ctx.logger.info("Checking Storage Account deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")

        ctx.node.properties[constants.STORAGE_DELETABLE_KEY] = False

        status_code = storage.create(ctx=ctx)
        ctx.logger.info("status_code : " + str(status_code))
        self.assertTrue(bool((status_code == 200) | (status_code == 202)))
        
        ctx.logger.info("create storage with deletable propertie set to false")
        
        status_storage = constants.CREATING
        while status_storage != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_storage = storage.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Storage Account status is " + status_storage)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Storage Account Created")
        self.assertEqual(constants.SUCCEEDED, status_storage)
        
        ctx.logger.info("not delete storage")
        self.assertEqual(0, storage.delete(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.STORAGE_DELETABLE_KEY] = True

        ctx.logger.info("Delete storage")
        self.assertEqual(200, storage.delete(ctx=ctx))

        ctx.logger.info("Checking Storage Account deleted")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")

        ctx.logger.info("END test delete storage")


    def test_conflict_storage(self):
        ctx = self.mock_ctx('testconflictstorage')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test conflict storage")

        status_code = storage.create(ctx=ctx)
        ctx.logger.info("status_code : " + str(status_code))
        self.assertTrue(bool((status_code == 200) | (status_code == 202)))

        status_storage = constants.CREATING
        while status_storage != constants.SUCCEEDED :
            current_ctx.set(ctx=ctx)
            status_storage = storage.get_provisioning_state(ctx=ctx)
            ctx.logger.info("Storage Account status is " + status_storage)
            time.sleep(TIME_DELAY)

        ctx.logger.info("Storage Account Created")
        self.assertEqual(constants.SUCCEEDED, status_storage)

        ctx.logger.info("Conflict Creating Storage Account")
        self.assertEqual(409, storage.create(ctx=ctx))

        self.assertEqual(200, storage.delete(ctx=ctx))

        ctx.logger.info("Check is Storage Account is release")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")

        ctx.logger.info("END test conflict storage")

    def __del__(self, *args):
        super(TestStorage, self).__init__(*args)

        ctx = self.mock_ctx('init')
        ctx.logger.info("CREATE storage_account\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)