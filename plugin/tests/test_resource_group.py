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
                    resource_group
                    )

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestResourceGroup(testtools.TestCase):

    __random_id = str(random.randrange(0, 1000, 2))
    
    @classmethod
    def setUpClass(self):
        ctx = self.mock_ctx('init')
        ctx.logger.info("BEGIN test ressource_group number " + self.__random_id)

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
                constants.RESOURCE_GROUP_KEY: test_name + self.__random_id,
            },
            constants.RESOURCE_GROUP_KEY: test_name + self.__random_id,
            constants.DELETABLE_KEY: True
        }

        return MockCloudifyContext(node_id = 'test' + self.__random_id,
                                   properties = test_properties)

    def setUp(self):
        super(TestResourceGroup, self).setUp()


    def tearDown(self):
        super(TestResourceGroup, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create_resource_group(self):
        ctx = self.mock_ctx('testcreategroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN resource_group create test")

        ctx.logger.info("create resource_group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, timeout=600)  

        current_ctx.set(ctx=ctx)
        ctx.logger.info("delete resource_group")
        self.assertEqual(202, resource_group.delete(ctx=ctx))
        
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "resource_group","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END resource_group create test")


    def test_delete_resource_group(self):
        ctx = self.mock_ctx('testdeletegroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN resource_group delete test")

        ctx.logger.info("create resource_group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, timeout=600)      

        current_ctx.set(ctx=ctx)
        ctx.logger.info("delete resource_group")
        self.assertEqual(202, resource_group.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "resource_group","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass


        ctx.logger.info("create resource_group with deletable propertie set to false")
        ctx.node.properties[constants.DELETABLE_KEY] = False
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, timeout=600)  

        ctx.logger.info("not delete resource_group")
        current_ctx.set(ctx=ctx)
        self.assertEqual(0, resource_group.delete(ctx=ctx))
        
        ctx.logger.info("delete resource_group")
        ctx.logger.info("Set deletable propertie to True")
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.DELETABLE_KEY] = True
        self.assertEqual(202, resource_group.delete(ctx=ctx))

        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "resource_group","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END resource_group delete test")

    def test_conflict_resource_group(self):
        ctx = self.mock_ctx('conflictgroup')
        current_ctx.set(ctx=ctx)
        ctx.logger.info("BEGIN resource_group conflict test")
        ctx.logger.info("create resource group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))
        current_ctx.set(ctx=ctx)
        utils.wait_status(ctx, "resource_group",constants.SUCCEEDED, timeout=600)    

        ctx.logger.info("conflict create resource group")
        status_code = resource_group.create(ctx=ctx)
        ctx.logger.debug("status_code = " + str(status_code) )
        self.assertTrue(bool((status_code == 200) or (status_code == 201)))

        ctx.logger.info("delete resource_group")
        current_ctx.set(ctx=ctx)
        self.assertEqual(202, resource_group.delete(ctx=ctx))
        
        try:
            current_ctx.set(ctx=ctx)
            utils.wait_status(ctx, "resource_group","waiting for exception", timeout=600)
        except utils.WindowsAzureError:
            pass

        ctx.logger.info("END resource_group conflict test")