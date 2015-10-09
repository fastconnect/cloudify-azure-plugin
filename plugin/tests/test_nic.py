# -*- coding: utf-8 -*-
import testtools
import time
import test_utils
import test_mockcontext
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    public_ip,
                    network,
                    subnet,
                    nic
                    )

from cloudify.state import current_ctx
from cloudify.mocks import (MockContext,
                            MockCloudifyContext,
                            MockNodeInstanceContext
                            )

TIME_DELAY = 20


class TestNIC(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))
 
    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test NIC number " + self.__random_id)
        ctx.logger.info("CREATE NIC\'s required resources")

        ctx.logger.info("CREATE ressource_group")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

        # ctx.logger.info("CREATE public_ip")
        # current_ctx.set(ctx=ctx)
        # ctx.node.properties[constants.PUBLIC_IP_KEY] = "nic_public_ip_test"
        # public_ip.create(ctx=ctx)
        
        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create(ctx=ctx)

        ctx.logger.info("CREATE subnet")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.SUBNET_ADDRESS_KEY] = "10.0.1.0/24"
        subnet.create(ctx=ctx)


    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("DELETE NIC\'s required resources")
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
                    'nic_resource_group_test' + self.__random_id,
                constants.VIRTUAL_NETWORK_KEY:\
                    'nic_virtual_network_test' + self.__random_id,
                constants.SUBNET_KEY:\
                    'nic_subnet_test' + self.__random_id
            },
            constants.RESOURCE_GROUP_KEY:\
                'nic_resource_group_test' + self.__random_id,
            constants.VIRTUAL_NETWORK_KEY:\
                'nic_virtual_network_test' + self.__random_id,
            constants.SUBNET_KEY:\
                'nic_subnet_test' + self.__random_id,
            constants.NETWORK_INTERFACE_KEY:\
                test_name + self.__random_id,
            constants.DELETABLE_KEY: True

        }
        #should not be empty 
        test_runtime = {
            'not': 'empty'
        }

        test_relationships = [
            {
                'node_id': 'test',
                'relationship_type': constants.SUBNET_CONNECTED_TO_NETWORK,
                'relationship_properties':\
                    {constants.VIRTUAL_NETWORK_KEY:\
                         'nic_virtual_network_test' + self.__random_id}
            },
            {
                'node_id': 'test',
                'relationship_type': constants.NIC_CONNECTED_TO_SUBNET,
                'relationship_properties':
                    {
                        constants.SUBNET_KEY: 'nic_subnet_test',
                        constants.VIRTUAL_NETWORK_KEY:\
                            'nic_virtual_network_test' + self.__random_id
                    }
            },
            # {
            #     'node_id': 'test',
            #     'relationship_type': constants.NIC_CONNECTED_TO_PUBLIC_IP,
            #     'relationship_properties': \
            #     {
            #         constants.PUBLIC_IP_KEY: 'nic_public_ip_test'
            #     }
            # }
        ]

        return test_mockcontext.MockCloudifyContextRelationships(node_id='test',
            properties=test_properties,
            runtime_properties=test_runtime,
            relationships=test_relationships
        )

    # @classmethod
    # def mock_relationship_ctx(self, test_name):
    #     """ Creates a mock relationship context for the nic
    #         tests
    #     """
    #
    #     source = MockContext({
    #         'node': MockContext({
    #             'properties': {
    #                 constants.AZURE_CONFIG_KEY:{
    #                     constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
    #                     constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
    #                     constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
    #                     constants.LOCATION_KEY: 'westeurope',
    #                     constants.RESOURCE_GROUP_KEY: 'nic_resource_group_test'
    #                 },
    #                 constants.RESOURCE_GROUP_KEY: 'nic_resource_group_test',
    #                 constants.NETWORK_INTERFACE_KEY: test_name,
    #                 constants.DELETABLE_KEY: True
    #             }
    #         })
    #     })
    #
    #     target = MockContext({
    #         'node': MockContext({
    #             'properties': {
    #                 constants.AZURE_CONFIG_KEY:{
    #                     constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
    #                     constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
    #                     constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
    #                     constants.LOCATION_KEY: 'westeurope',
    #                     constants.RESOURCE_GROUP_KEY: 'nic_resource_group_test'
    #                 },
    #                 constants.RESOURCE_GROUP_KEY: 'nic_resource_group_test',
    #                 constants.PUBLIC_IP_KEY: 'nic_public_ip_test',
    #                 constants.DELETABLE_KEY: True
    #             }
    #         })
    #     })
    #
    #     return test_mockcontext.MockCloudifyContextRelationships(
    #         node_id='test',
    #         source=source,
    #         target=target
    #     )

    def setUp(self):
        super(TestNIC, self).setUp()


    def tearDown(self):
        super(TestNIC, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create(self):
        ctx = self.mock_ctx('testcreatenic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create NIC test")

        ctx.logger.info("create NIC")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)  

        ctx.logger.info("delete NIC")
        self.assertEqual(202, nic.delete(ctx=ctx))

        ctx.logger.info("check is NIC is release")
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "nic","deleting", 600)
        except utils.WindowsAzureError:
            pass
        
        ctx.logger.info("END create NIC test")


    # def test_add_public_ip(self):
    #     ctx = self.mock_ctx('testaddpublicip')
    #     current_ctx.set(ctx=ctx)
    #     ctx.logger.info("BEGIN attach public_ip to NIC test")
    #
    #     ctx.logger.info("create NIC")
    #     nic.create(ctx=ctx)
    #     current_ctx.set(ctx=ctx)
    #     utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)
    #
    #     ctx.logger.info("attach public_ip to NIC: {}".format(ctx.instance.runtime_properties['subnet_id']))
    #
    #     ctx_rel = self.mock_relationship_ctx('testaddpublicip', str(ctx.instance.runtime_properties['subnet_id']))
    #     current_ctx.set(ctx=ctx_rel)
    #     ctx_rel.logger.info("Source node NIC key: {}".format(ctx_rel.source.node.properties[constants.NETWORK_INTERFACE_KEY]))
    #     nic.add_public_ip(ctx=ctx_rel)
    #
    #     current_ctx.set(ctx=ctx)
    #     utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)
    #
    #     ctx.logger.info("delete NIC")
    #     self.assertEqual(202, nic.delete(ctx=ctx))
    #
    #     ctx.logger.info("check is NIC is release")
    #     current_ctx.set(ctx=ctx)
    #     self.assertRaises(utils.WindowsAzureError,
    #                       nic.get_provisioning_state,
    #                       ctx=ctx
    #                       )
    #
    #     ctx.logger.info("END create NIC test")


    def test_delete(self):
        ctx = self.mock_ctx('testdeletenic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete NIC test")

        ctx.logger.info("create NIC")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)  

        ctx.logger.info("trying to delete an non-deletable nic")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        current_ctx.set(ctx=ctx)
        self.assertEqual(0, nic.delete(ctx=ctx))

        ctx.logger.info("delete NIC")
        ctx.node.properties[constants.DELETABLE_KEY] = True
        current_ctx.set(ctx=ctx)
        self.assertEqual(202, nic.delete(ctx=ctx))

        ctx.logger.info("check is nic is release")
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "nic","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END delete NIC test")


    def test_conflict(self):
        ctx = self.mock_ctx('testconflictnic')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict NIC test")

        ctx.logger.info("create NIC")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "nic",constants.SUCCEEDED, 600)  

        ctx.logger.info("create NIC conflict")
        status_code = nic.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        ctx.logger.info("delete NIC")
        self.assertEqual(202, nic.delete(ctx=ctx))

        ctx.logger.info("check is NIC is release")
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "nic","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("delete conflict NIC")
        self.assertEqual(204, nic.delete(ctx=ctx))

        ctx.logger.info("END conflict NIC  test")