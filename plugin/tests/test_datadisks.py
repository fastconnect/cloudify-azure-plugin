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


class TestDatadisks(testtools.TestCase):

    def mock_ctx(self, test_name, disk):
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
            constants.COMPUTE_KEY: test_name,
            constants.COMPUTE_USER_KEY: test_utils.COMPUTE_USER,
            constants.COMPUTE_PASSWORD_KEY: test_utils.COMPUTE_PASSWORD,
            constants.PUBLIC_KEY_KEY: test_utils.PUBLIC_KEY,
            constants.PRIVATE_KEY_KEY: test_utils.PRIVATE_KEY,
            constants.STORAGE_ACCOUNT_KEY: 'storageaccounttest3',
            constants.CREATE_OPTION_KEY:'FromImage',
            constants.RESOURCE_GROUP_KEY: 'resource_group_test',
            constants.VIRTUAL_NETWORK_KEY: 'management_network_test',
            constants.SUBNET_KEY: 'subnet_test',
            constants.DISKS_KEY: disk,
            'resources_prefix': 'boulay',
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def test_create_datadisk(self):
        disk = [{'name': 'disk_1',
                 'size': 100,
                 'attach': False,
                 'caching': 'None'
               }]

        test_name = 'test-create-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name)) 

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance')

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        ctx.logger.debug(json_VM)

        self.assertIsNotNone(json_VM['properties']['storageProfile']['dataDisks'])
        
        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertEqual(disk[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disk[0]['caching'], disks_vm[0]['caching'])
        self.assertEqual(disk[0]['size'], disks_vm[0]['diskSizeGB'])

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name)) 
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', constants.DELETING)
        except utils.WindowsAzureError:
            pass

    def test_create_dataDisks(self):
        disks = [{'name': 'disks_1',
                  'size': 100,
                  'attach': False,
                  'caching': 'None'
                },{'name': 'disks_2',
                   'size': 200,
                   'attach': False,
                   'caching': 'ReadWrite'
                }]

        test_name = 'test-create-datadisks'
        ctx = self.mock_ctx(test_name, disks)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance')

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        self.assertIsNotNone(json_VM['properties']['storageProfile']['dataDisks'])

        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertEqual(disks[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disks[0]['size'], disks_vm[0]['diskSizeGB'])
        self.assertEqual(disks[0]['caching'], disks_vm[0]['caching'])

        self.assertEqual(disks[1]['name'], disks_vm[1]['name'])
        self.assertEqual(disks[1]['size'], disks_vm[1]['diskSizeGB'])
        self.assertEqual(disks[1]['caching'], disks_vm[1]['caching'])

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', constants.DELETING)
        except utils.WindowsAzureError:
            pass

    def test_create_too_much_datadisks(self):
        disks = [{'name': 'much_disks_1',
                  'size': 100,
                  'attach': False,
                  'caching': 'None'
                },{'name': 'much_disks_2',
                   'size': 200,
                   'attach': False,
                   'caching': 'ReadWrite'
                },{'name': 'much_disks_3',
                   'size': 200,
                   'attach': False,
                   'caching': 'ReadOnly'
                }]

        test_name = 'test-create-too-much-datadisks'
        ctx = self.mock_ctx(test_name , disks)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name)) 

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance')

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        self.assertIsNotNone(json_VM['properties']['storageProfile']['dataDisks'])

        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertNotEqual(len(disks), len(disks_vm))

        self.assertEqual(disks[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disks[0]['size'], disks_vm[0]['diskSizeGB'])
        self.assertEqual(disks[0]['caching'], disks_vm[0]['caching'])

        self.assertEqual(disks[1]['name'], disks_vm[1]['name'])
        self.assertEqual(disks[1]['size'], disks_vm[1]['diskSizeGB'])
        self.assertEqual(disks[1]['caching'], disks_vm[1]['caching'])

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', constants.DELETING)
        except utils.WindowsAzureError:
            pass

    def test_fail_create_datadisk(self):
        disk = [{'name': 'disk_fail_1',
                 'size': 100,
                 'attach': True,
                 'caching': 'None'
               }]

        test_name = 'test-fail-create-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name)) 

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance')

        current_ctx.set(ctx=ctx)
        self.assertRaises(NonRecoverableError,
                          datadisks.create,
                          ctx=ctx
                          )

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name)) 
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', constants.DELETING)
        except utils.WindowsAzureError:
            pass

    def test_attach_datadisk(self):
        disk = [{'name': 'attach_disk',
                  'size': 100,
                  'attach': False,
                  'caching': 'None'
                }]

        test_name = 'test-attach-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'instance')

        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', constants.DELETING)
        except utils.WindowsAzureError:
            pass

        disk[0]['attach'] = True

        test_name = 'test-attach-datadisk'
        ctx = self.mock_ctx(test_name, disk)
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create VM test: {}".format(test_name))

        instance.create(ctx=ctx)
        
        current_ctx.set(ctx=ctx)
        datadisks.create(ctx=ctx)

        current_ctx.set(ctx=ctx)
        json_VM = instance.get_json_from_azure(ctx=ctx)

        ctx.logger.debug(json_VM)

        self.assertIsNotNone(json_VM['properties']['storageProfile']['dataDisks'])
        
        disks_vm = json_VM['properties']['storageProfile']['dataDisks']

        ctx.logger.debug(disks_vm)

        self.assertEqual(disk[0]['name'], disks_vm[0]['name'])
        self.assertEqual(disk[0]['caching'], disks_vm[0]['caching'])
        self.assertEqual(disk[0]['size'], disks_vm[0]['diskSizeGB'])
        
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete VM test: {}".format(test_name))
        instance.delete(ctx=ctx)

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, 'instance', constants.DELETING)
        except utils.WindowsAzureError:
            pass


