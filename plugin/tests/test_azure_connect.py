import testtools
import requests
import test_utils

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from azure.servicemanagement import ServiceManagementService

from plugin import connection
from plugin import constants
from plugin.utils import WindowsAzureError


class TestConnection(testtools.TestCase):

    def get_mock_context(self, test_name):
        """ Creates a mock context."""

        return MockCloudifyContext(
            node_id=test_name,
            properties={
                'username': test_utils.AZURE_USERNAME,
                'password': test_utils.AZURE_PASSWORD,
                'subscription_id': test_utils.SUBSCRIPTION_ID
            }
        )


    def test_connect(self):
        """ this tests that a the correct region endpoint
        in returned by the connect function
        """

        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        self.assertIsNotNone(connection.AzureConnectionClient())


    def test_connect_fails(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)
        ctx.node.properties['password'] = 'wrong'

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
                    ctx.node.properties['subscription_id'],
                    constants.AZURE_API_VERSION_01
                    )
                ).json()
        ctx.logger.debug(json)
        self.assertIsNotNone(json)
        self.assertEqual(json['subscriptionId'], 
                         ctx.node.properties['subscription_id']
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
                        ctx.node.properties['subscription_id'],
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
                                ctx.node.properties['subscription_id']
                                )
                          )


    def test_azure_delete(self):
        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_connection = connection.AzureConnectionClient()
        response = azure_connection.azure_delete(
                    ctx,
                    'subscriptions/{}/tagNames/{}?api-version={}'.format(
                        ctx.node.properties['subscription_id'],
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
                                ctx.node.properties['subscription_id']
                                )
                          )