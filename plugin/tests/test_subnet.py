# -*- coding: utf-8 -*-
import testtools
import time
import test_utils
import test_mockcontext
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    subnet,
                    network,
                    security_group
                    )

from cloudify.state import current_ctx

TIME_DELAY = 20

class TestSubnet(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))

    @classmethod
    def setUpClass(self): 
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test subnet number " + self.__random_id)

        ctx.logger.info("CREATE resource_group")        
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

        ctx.logger.info("CREATE network")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[
            constants.VIRTUAL_NETWORK_ADDRESS_KEY] = "10.0.0.0/16"
        network.create(ctx=ctx)

    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        ctx.logger.info("DELETE subnet\'s required resources")
        
        ctx.logger.info("DELETE resource_group")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)

    @classmethod
    def mock_ctx(self, test_name, cdir='10.0.1.0/24'):
        """ Creates a mock context for the instance
            tests
        """
        test_properties = {
            constants.AZURE_CONFIG_KEY:{
                constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID,
                constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                constants.LOCATION_KEY: 'westeurope',
                constants.RESOURCE_GROUP_KEY:\
                    'subnetresource_group_test' + self.__random_id
            },
            constants.RESOURCE_GROUP_KEY: 'subnetresource_group_test' + self.__random_id,
            constants.SUBNET_KEY: test_name + self.__random_id,
            constants.SUBNET_ADDRESS_KEY: cdir,
            constants.VIRTUAL_NETWORK_KEY: 'subnetnetwork_test'+self.__random_id,
            constants.SECURITY_GROUP_KEY: 'subnetsecugroup_test' + self.__random_id,
            constants.RULES_KEY: {
                'subnet_rule_test' + self.__random_id: {}
            },
            constants.DELETABLE_KEY: True
        }

        test_runtime = {
            constants.VIRTUAL_NETWORK_KEY: 'subnetnetwork_test' + self.__random_id
        }

        test_relationships = [ 
            {
                'node_id': 'test',
                'relationship_type': constants.SUBNET_CONNECTED_TO_NETWORK,
                'relationship_properties': {
                    constants.VIRTUAL_NETWORK_KEY: 'subnetnetwork_test' + self.__random_id
                }
            }
        ]

        return test_mockcontext.MockCloudifyContextRelationships(
                                node_id='test',
                                properties=test_properties,
                                runtime_properties=test_runtime,
                                relationships=test_relationships
                                )


    def setUp(self):
        super(TestSubnet, self).setUp()

    def tearDown(self):
        super(TestSubnet, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create_subnet(self):
        ctx = self.mock_ctx('testcreatesubnet', cdir='10.0.2.0/24')
        ctx.logger.info("BEGIN test_create_subnet")

        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, timeout=600)

        current_ctx.set(ctx=ctx)
        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "subnet", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END test_create_subnet")

    def test_connect_security_group_subnet(self):
        ctx = self.mock_ctx('testaddsecugroupsubnet', cdir='10.0.5.0/24')
        ctx.logger.info("BEGIN test_connect_security_group_subnet")

        ctx.logger.info("create security_group")
        self.assertEqual(201, security_group.create(ctx=ctx))
        ctx.logger.debug("security_group_id = {}".format(
            ctx.instance.runtime_properties[constants.SECURITY_GROUP_ID_KEY]))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, 'security_group', constants.SUCCEEDED, timeout=900)

        ctx.instance.relationships.append(test_mockcontext.MockRelationshipContext(node_id='test',
            runtime_properties={
                constants.SECURITY_GROUP_ID_KEY:\
                     ctx.instance.runtime_properties[constants.SECURITY_GROUP_ID_KEY]
            },
            type=constants.SUBNET_CONNECTED_TO_SECURITY_GROUP)
        )

        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, timeout=600)

        ctx.logger.info("test subnet is connected to a security_group")
        current_ctx.set(ctx=ctx)
        json = subnet.get_json_from_azure(ctx=ctx)
        self.assertIsNotNone(json['properties']['networkSecurityGroup'])
        self.assertEqual(str(json['properties']['networkSecurityGroup']['id']).lower(),
            str(ctx.instance.runtime_properties[constants.SECURITY_GROUP_ID_KEY]).lower()
        )

        current_ctx.set(ctx=ctx)
        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "subnet", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("delete security_group")
        self.assertEqual(202, security_group.delete(ctx=ctx))

        ctx.logger.info("END test_connect_security_group_subnet")

    def test_delete_subnet(self):
        ctx = self.mock_ctx('testdeletesubnet', cdir='10.0.3.0/24')
        ctx.logger.info("BEGIN test_delete_subnet")

        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, timeout=600)

        current_ctx.set(ctx=ctx)
        ctx.logger.info("create subnet with deletable propertie set to False")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        ctx.logger.info("not delete subnet")
        self.assertEqual(0, subnet.delete(ctx=ctx))

        current_ctx.set(ctx=ctx)
        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True
        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "subnet", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass
          
        ctx.logger.info("END test_delete_subnet")

    def test_conflict_subnet(self):
        ctx = self.mock_ctx('testconflictsubnet', cdir='10.0.4.0/24')
        ctx.logger.info("BEGIN test_conflict_subnet")

        current_ctx.set(ctx=ctx)
        status_code = subnet.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "subnet",constants.SUCCEEDED, timeout=600)

        ctx.logger.info("Conflict Creating Subnet")
        current_ctx.set(ctx=ctx)
        self.assertNotEqual(201, subnet.create(ctx=ctx))
        ctx.logger.info("Conflict detected")

        current_ctx.set(ctx=ctx)
        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))
    
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "subnet", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass
        ctx.logger.info("Subnet Deleted")
        
        current_ctx.set(ctx=ctx)
        status_code = subnet.delete(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 202) or (status_code == 204)))
     
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "subnet", "waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("Virtual subnet Deleted")
        ctx.logger.info("END test_conflict_subnet")