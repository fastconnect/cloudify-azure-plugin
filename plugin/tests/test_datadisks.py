import test_utils
import testtools

from plugin import (utils,
                    constants,
                    resource_group,
                    storage,
                    network,
                    subnet,
                    public_ip,
                    nic,
                    datadisks,
                    instance
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

class TestDatadisks(testtools.TestCase):

    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init','')    
        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE ressource_group")
        resource_group.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group", constants.SUCCEEDED, 600)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("CREATE storage account")
        ctx.node.properties[constants.ACCOUNT_TYPE_KEY] = "Standard_LRS"
        storage.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "storage",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "network",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE subnet")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] = "10.0.1.0/24"
        ctx.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] = "diskvirtualnetwork_test"

        subnet.create(ctx=ctx) 
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, 600)
      
        ctx.logger.info("CREATE public_ip")
        current_ctx.set(ctx=ctx)
        ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = "diskpublic_ip_test"
        public_ip.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, 600)

        ctx.logger.info("CREATE NIC")
        current_ctx.set(ctx=ctx)
        ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY] = "disknic_test"
        ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = "diskpublic_ip_test"
        nic.create(ctx=ctx)
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)

        
    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del','')

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE nic")
        ctx.instance.runtime_properties[constants.NETWORK_INTERFACE_KEY] = "disknic_test"
        ctx.node.properties[constants.DELETABLE_KEY] = True
        nic.delete(ctx=ctx)

        try:
            utils.wait_status(ctx, "nic","wait for exception", 600)          
        except utils.WindowsAzureError:
            pass
     
        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE public_ip")
        ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY] = "diskpublic_ip_test"
        ctx.node.properties[constants.DELETABLE_KEY] = True
        public_ip.delete(ctx=ctx)
        
        try:
            utils.wait_status(ctx, "public_ip","wait for exception", 600)          
        except utils.WindowsAzureError:
            pass

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE subnet")
        ctx.instance.runtime_properties[constants.VIRTUAL_NETWORK_KEY] = "diskvirtualnetwork_test"
        subnet.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE network")
        network.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE storage account")
        storage.delete(ctx=ctx)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("DELETE ressource_group")
        resource_group.delete(ctx=ctx)

 
    @classmethod 
    def mock_ctx(self, test_name, disk):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY: 'diskresource_group_test'
            },
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
            constants.STORAGE_ACCOUNT_KEY: 'diskstorageaccounttest',
            constants.CREATE_OPTION_KEY:'FromImage',
            constants.RESOURCE_GROUP_KEY: 'diskresource_group_test',
            constants.VIRTUAL_NETWORK_KEY: 'diskvirtualnetwork_test',
            constants.SUBNET_KEY: 'disksubnet_test',
            constants.NETWORK_INTERFACE_KEY: 'disknic_test',
            constants.DISKS_KEY: disk,
            'resources_prefix': 'diskprefix',
            constants.DELETABLE_KEY: True

        }
        test_runtime = {
            constants.PUBLIC_IP_KEY: 'diskpublic_ip_test',
            constants.VIRTUAL_NETWORK_KEY: 'diskvirtualnetwork_test',
            constants.NETWORK_INTERFACE_KEY: 'disknic_test'
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
        utils.wait_status(ctx, 'instance', constants.CREATING, 900)

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
        self.assertEqual(202, instance.delete(ctx=ctx))

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
        utils.wait_status(ctx, "instance",constants.SUCCEEDED, 900)

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
            utils.wait_status(ctx, 'instance', constants.DELETING, 900)
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

