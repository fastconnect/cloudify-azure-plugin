import testtools
import time
import test_utils

try:
    from plugin import utils
    from plugin import constants
    from plugin import connection
    from plugin import ressource_group
except:
    import utils
    import constants
    import connection
    import ressource_group

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestRessourceGroup(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription_id': test_utils.SUBSCRIPTION_ID,
            'username': test_utils.AZURE_USERNAME, 
            'password': test_utils.AZURE_PASSWORD,
            'location': 'westeurope',
            'resource_group_name': test_name
        }

        return MockCloudifyContext(node_id = 'test',
                                   properties = test_properties)

    def setUp(self):
        super(TestRessourceGroup, self).setUp()


    def tearDown(self):
        super(TestRessourceGroup, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create_ressource_group(self):
        ctx = self.mock_ctx('testcreategroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create ressource_group test")

        ctx.logger.info("create ressource_group")
        status_code = ressource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_ressource_group = constants.CREATING
        while status_ressource_group == constants.CREATING :
            current_ctx.set(ctx=ctx)
            ctx.logger.debug(status_ressource_group)
            status_ressource_group = ressource_group.get_ressource_group_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.debug(status_ressource_group)
        ctx.logger.info("check ressource_group creation success")
        self.assertEqual( constants.SUCCEEDED, status_ressource_group)

        ctx.logger.info("delete ressource_group")
        self.assertEqual(202, ressource_group.delete(ctx=ctx))

        try:
            while status_ressource_group == constants.DELETING :
                current_ctx.set(ctx=ctx)
                ctx.logger.debug(status_ip)           
                status_ressource_group = ressource_group.get_ressource_group_provisioning_state(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END create ressource_group  test")


    def test_delete_ressource_group(self):
        ctx = self.mock_ctx('testdeletegroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create ressource_group test")

        ctx.logger.info("create ressource_group")
        status_code = ressource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_ressource_group = constants.CREATING
        while status_ressource_group == constants.CREATING :
            current_ctx.set(ctx=ctx)
            ctx.logger.debug(status_ressource_group)
            status_ressource_group = ressource_group.get_ressource_group_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.debug(status_ressource_group)
        ctx.logger.info("check ressource_group creation success")
        self.assertEqual( constants.SUCCEEDED, status_ressource_group)

        ctx.logger.info("delete ressource_group")
        self.assertEqual(202, ressource_group.delete(ctx=ctx))

        try:
            while status_ressource_group == constants.DELETING :
                current_ctx.set(ctx=ctx)
                ctx.logger.debug(status_ip)           
                status_ressource_group = ressource_group.get_ressource_group_provisioning_state(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END create ressource_group  test")


    def test_conflict_ressource_group(self):
        ctx = self.mock_ctx('conflictgroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict ressource_group test")

        ctx.logger.info("create ressource group")
        status_code = ressource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        status_ressource_group = constants.CREATING
        while status_ressource_group == constants.CREATING :
            current_ctx.set(ctx=ctx)
            ctx.logger.debug(status_ressource_group)
            status_ressource_group = ressource_group.get_ressource_group_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)

        ctx.logger.info("conflict create ressource group")
        status_code = ressource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))


        ctx.logger.info("delete ressource_group")
        self.assertEqual(202, ressource_group.delete(ctx=ctx))

        try:
            while status_ressource_group == constants.DELETING :
                current_ctx.set(ctx=ctx)
                ctx.logger.debug(status_ip)           
                status_ressource_group = ressource_group.get_ressource_group_provisioning_state(ctx=ctx)
                time.sleep(TIME_DELAY)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("conflict delete ressource_group")
        self.assertEqual(202, ressource_group.delete(ctx=ctx))