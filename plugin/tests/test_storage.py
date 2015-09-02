import testtools
import time
import test_utils

from plugin import (utils,
                    constants,
                    storage,
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestStorage(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': test_utils.SUBSCRIPTION_ID,
            'username': test_utils.AZURE_USERNAME,
            'password': test_utils.AZURE_PASSWORD,
            'location': 'westeurope',
            'resource_group_name': 'cloudifygroup',
            'storage_account_name': test_name,
            'account_type': 'Standard_LRS' #Standard_LRS|Standard_ZRS|Standard_GRS|Standard_RAGRS|Premium_LRS
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
        ctx.logger.info("BEGIN test_create_storage")

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
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")
        ctx.logger.info("END test_create_storage")
        #self.assertTrue(False)


    def test_delete_storage(self):
        ctx = self.mock_ctx('testdeletestorage')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_delete_storage")

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
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")
        ctx.logger.info("END test_delete_storage")
        #self.assertTrue(False)


    def test_conflict_storage(self):
        ctx = self.mock_ctx('testconflictstorage')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN test_conflict_storage")

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

        ctx.logger.info("check is Storage Account is release")
        self.assertRaises(utils.WindowsAzureError,
            storage.get_provisioning_state,
            ctx=ctx
        )
        ctx.logger.info("Storage Account Deleted")

        ctx.logger.info("END test_conflict_storage")
        #self.assertTrue(False)