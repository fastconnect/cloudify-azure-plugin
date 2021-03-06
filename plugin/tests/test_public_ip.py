# -*- coding: utf-8 -*-
########
# Copyright (c) 2015 Fastconnect - Atost. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import testtools
import time
import test_utils
import random

from plugin import (utils,
                    constants,
                    resource_group,
                    public_ip
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestPublicIP(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))
    
    @classmethod
    def setUpClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test public_ip number " + self.__random_id)
        ctx.logger.info("CREATE public_ip\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.create(ctx=ctx)


    @classmethod
    def tearDownClass(self):
        ctx = self.mock_ctx('del')
        ctx.logger.info("DELETE public_ip\'s required resources")
        current_ctx.set(ctx=ctx)
        resource_group.delete(ctx=ctx)

    
    @classmethod
    def mock_ctx(self, test_name):
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
                    'publicipresource_group_test' + self.__random_id
            },
            constants.RESOURCE_GROUP_KEY:\
                'publicipresource_group_test' + self.__random_id,
            constants.PUBLIC_IP_KEY: test_name + self.__random_id,
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
        super(TestPublicIP, self).setUp()


    def tearDown(self):
        super(TestPublicIP, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_public_ip(self):
        ctx = self.mock_ctx('testcreateip')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN create public_ip test")

        ctx.logger.info("create public_ip")
        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, timeout=600)    

        ctx.logger.info("delete public_ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "public_ip","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END create public_ip test")


    def test_delete_public_ip(self):
        ctx = self.mock_ctx('testdeleteip')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN public_ip delete test")

        ctx.logger.info("create public ip with deletable propertie set to False")
        ctx.node.properties[constants.DELETABLE_KEY] = False

        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, timeout=600)

        ctx.logger.info("not delete public ip")
        self.assertEqual(0, public_ip.delete(ctx=ctx))

        ctx.logger.info("Set deletable propertie to True")
        ctx.node.properties[constants.DELETABLE_KEY] = True

        ctx.logger.info("delete public ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "public_ip","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END public_ip delete test")


    def test_conflict_public_ip(self):
        ctx = self.mock_ctx('testconflictip')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN conflict public_ip test")

        ctx.logger.info("create public_ip")
        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "public_ip",constants.SUCCEEDED, timeout=600)

        status_code = public_ip.create(ctx=ctx)
        ctx.logger.debug("status_code =" + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        ctx.logger.info("delete public_ip")
        self.assertEqual(202, public_ip.delete(ctx=ctx))
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "public_ip","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("delete conflict public_ip")
        self.assertEqual(204, public_ip.delete(ctx=ctx))
        
        ctx.logger.info("END conflict public_ip test")