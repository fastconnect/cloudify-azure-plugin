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
import requests
import test_utils
import time

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

from plugin import (connection,
                    constants
                    )
from plugin.utils import WindowsAzureError


class TestConnection(testtools.TestCase):

    @staticmethod
    def get_mock_context(test_name):
        """ Creates a mock context."""

        return MockCloudifyContext(
            node_id=test_name,
            properties={
                constants.AZURE_CONFIG_KEY:{
                    constants.USERNAME_KEY: test_utils.AZURE_USERNAME,
                    constants.PASSWORD_KEY: test_utils.AZURE_PASSWORD,
                    constants.SUBSCRIPTION_KEY: test_utils.SUBSCRIPTION_ID
                }
           }
        )

    def test_connect(self):
        """ this tests that a the correct region endpoint
        in returned by the connect function
        """

        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        cnt = connection.AzureConnectionClient()
        self.assertIsNotNone(cnt)
        self.assertIsNotNone(connection.AzureConnectionClient.token)
        self.assertIsNotNone(connection.AzureConnectionClient.expires_on)

    def test_reuse_token(self):
        ctx = self.get_mock_context('test_reuse_token')
        current_ctx.set(ctx=ctx)
        cnt = connection.AzureConnectionClient()
        token = connection.AzureConnectionClient.token

        time.sleep(constants.TIME_DELAY)

        cnt = connection.AzureConnectionClient()
        self.assertEqual(token, connection.AzureConnectionClient.token)


    def test_connect_fails(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)
        ctx.node.properties[constants.AZURE_CONFIG_KEY
                            ][constants.PASSWORD_KEY] = 'wrong'

        connection.AzureConnectionClient.token = None
        self.assertRaises(WindowsAzureError, 
                          connection.AzureConnectionClient
                          )

    def test_azure_get(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()
        json = azure_connection.azure_get(
                ctx,
                'subscriptions/{}?api-version={}'.format(
                    ctx.node.properties[constants.AZURE_CONFIG_KEY
                                        ][constants.SUBSCRIPTION_KEY],
                    constants.AZURE_API_VERSION_01
                    )
                ).json()
        ctx.logger.debug(json)
        self.assertIsNotNone(json)
        self.assertEqual(json['subscriptionId'], 
                         ctx.node.properties[constants.AZURE_CONFIG_KEY
                                             ][constants.SUBSCRIPTION_KEY]
                         )


    def test_azure_get_fails(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()
        self.assertRaises(WindowsAzureError,
                          azure_connection.azure_get,
                          ctx, 
                          'subscriptions/3121df85-fac7-48ec-bd49-08c257068600'
                          )

    def test_azure_post(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()

        data = {'Name':'notexist',
                'Type':'storageaccounts'}

        json = azure_connection.azure_post(
            ctx, 
            'providers/microsoft.resources/checkresourcename?api-version={}'.\
                format(constants.AZURE_API_VERSION_01),
            data
            ).json()

        self.assertEqual(json['status'], 'Allowed')

    def test_azure_post_fails(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()

        data = {'Namen':'Microsoft',
                'Type':'storageaccounts'}

        self.assertRaises(WindowsAzureError,
                          azure_connection.azure_post,
                          ctx, 
                          'providers/microsoft.resources/checkresourcename',
                          data
                          )

    def test_azure_put(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()

        json = azure_connection.azure_put(
                ctx,
                'subscriptions/{}/tagNames/{}?api-version={}'.format(
                        ctx.node.properties[constants.AZURE_CONFIG_KEY
                                           ][constants.SUBSCRIPTION_KEY],
                        'test_tag',
                        constants.AZURE_API_VERSION_01
                        )
                 ).json()

        self.assertEqual(json['tagName'], 'test_tag')


    def test_azure_put_fails(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()

        self.assertRaises(WindowsAzureError,
                          azure_connection.azure_put,
                          ctx, 
                          'subscriptions/{}/tagName/test tag'.format(
                                ctx.node.properties[constants.AZURE_CONFIG_KEY
                                                 ][constants.SUBSCRIPTION_KEY]
                                )
                          )


    def test_azure_delete(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()
        response = azure_connection.azure_delete(
                    ctx,
                    'subscriptions/{}/tagNames/{}?api-version={}'.format(
                        ctx.node.properties[constants.AZURE_CONFIG_KEY
                                           ][constants.SUBSCRIPTION_KEY],
                        'test_tag',
                        constants.AZURE_API_VERSION_01
                        )
                    )

        self.assertRegexpMatches(str(response.status_code), r'(^2+)')


    def test_azure_delete_fails(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()

        self.assertRaises(WindowsAzureError,
                          azure_connection.azure_delete,
                          ctx, 
                          'subscriptions/{}/tagName/test tag'.format(
                                ctx.node.properties[constants.AZURE_CONFIG_KEY
                                                  ][constants.SUBSCRIPTION_KEY]
                                )
                          )