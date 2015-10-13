# -*- coding: utf-8 -*-
import testtools
import time
import test_utils
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    network,
                    subnet,
                    security_group
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestSecurityGroup(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))

    @classmethod
    def setUpClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test security_group number " + self.__random_id)
        ctx.logger.info("CREATE security group required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)

    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        ctx.logger.info("DELETE security group required resources")
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
                    'secu_group_res_group_test' + self.__random_id,
            },
            constants.RESOURCE_GROUP_KEY:\
                'secu_group_res_group_test' + self.__random_id,
            constants.SECURITY_GROUP_KEY: test_name + self.__random_id,
            constants.DELETABLE_KEY: True,
            constants.RULES_KEY: [
                {
                    constants.RULE_KEY: 'secu_group_rule_1_test' + self.__random_id
                },
                {
                    constants.RULE_KEY: 'secu_group_rule_2_test' + self.__random_id,
                    constants.PROTOCOL_KEY: 'Udp',
                    constants.SOURCE_PORT_KEY: '20-3000',
                    constants.DEST_PORT_KEY: '21',
                    constants.SOURCE_ADDRESS_KEY: '69.69.69.69',
                    constants.DEST_ADDRESS_KEY: '10.0.0.0/8',
                    constants.ACCESS_KEY: 'Allow',
                    constants.DIRECTION_KEY: 'Outbound'
                },
            ]
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
        super(TestSecurityGroup, self).setUp()


    def tearDown(self):
        super(TestSecurityGroup, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_security_group(self):
        ctx = self.mock_ctx('testcreatesecuritygroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create security_group test")

        ctx.logger.info("create security_group")
        self.assertEqual(201, security_group.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "security_group",constants.SUCCEEDED, 600)

        ctx.logger.info("delete security_group")
        self.assertEqual(202, security_group.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "security_group","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END create security_group test")


    def test_delete_security_group(self):
        ctx = self.mock_ctx('testdeletesecuritygroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN delete security_group test")

        ctx.logger.info("create security_group")
        self.assertEqual(201, security_group.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "security_group",constants.SUCCEEDED, 600)

        ctx.logger.info("trying to delete an non-deletable security_group")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        current_ctx.set(ctx=ctx)
        self.assertEqual(0, security_group.delete(ctx=ctx))

        ctx.logger.info("delete security_group")
        ctx.node.properties[constants.DELETABLE_KEY] = True
        current_ctx.set(ctx=ctx)
        self.assertEqual(202, security_group.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "security_group","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END delete security_group test")


    def test_conflict_security_group(self):
        ctx = self.mock_ctx('testconflictsecuritygroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict security_group test")

        ctx.logger.info("create security_group")
        self.assertEqual(201, security_group.create(ctx=ctx))

        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "security_group",constants.SUCCEEDED, 600)

        ctx.logger.info("create conflict security_group")
        self.assertEqual(200, security_group.create(ctx=ctx))

        ctx.logger.info("delete security_group")
        self.assertEqual(202, security_group.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "security_group","deleting", 600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("delete conflict security_group")
        self.assertEqual(204, security_group.delete(ctx=ctx))

        ctx.logger.info("END conflict security_group test")