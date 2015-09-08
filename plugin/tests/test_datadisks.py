import test_utils
import testtools

from plugin import (utils,
                    constants,
                    datadisks,
                    instance
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError


class TestInstance(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
            constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
            constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
            constants.LOCATION_KEY: 'westeurope',
            constants.PUBLISHER_KEY: 'Canonical',
            constants.OFFER_KEY: 'UbuntuServer',
            constants.SKU_KEY: '12.04.5-LTS',
            constants.SKU_VERSION_KEY: 'latest',
            constants.FLAVOR_KEY: 'Standard_A1',
            constants.COMPUTE_KEY: 'test-datadisk2',
            constants.COMPUTE_USER_KEY: test_utils.COMPUTE_USER,
            constants.COMPUTE_PASSWORD_KEY: test_utils.COMPUTE_PASSWORD,
            constants.PUBLIC_KEY_KEY: test_utils.PUBLIC_KEY,
            constants.PRIVATE_KEY_KEY: test_utils.PRIVATE_KEY,
            constants.STORAGE_ACCOUNT_KEY: 'storageaccounttest3',
            constants.CREATE_OPTION_KEY:'FromImage',
            constants.RESOURCE_GROUP_KEY: 'resource_group_test',
            constants.VIRTUAL_NETWORK_KEY: 'management_network_test',
            constants.SUBNET_KEY: 'subnet_test',
            constants.DISKS_KEY: [{'name': test_name,
                                   'size': 100,
                                   'caching': 'None'
                                 }],
            'resources_prefix': 'boulay',
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def test_create_datadisk(self):
        ctx = self.mock_ctx('testcreatedatadisks')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(ctx.instance.id))
        ctx.logger.info("create VM")    

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance')

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        jsonVM = instance.get_json_from_azure(ctx=ctx)

        self.assertIsNotNone(jsonVM['properties']['storageProfile']['dataDisks'])

        current_ctx.set(ctx=ctx)
        instance.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance', constants.DELETING)
