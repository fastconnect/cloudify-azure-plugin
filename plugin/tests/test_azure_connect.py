import testtools

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from azure.servicemanagement import ServiceManagementService

from plugin import connection
from plugin import constants

class TestConnection(testtools.TestCase):

    def get_mock_context(self, test_name):
        """ Creates a mock context."""

        return MockCloudifyContext(
            node_id=test_name,
            properties={
                'subscription': '3121df85-fac7-48ec-bd49-08c2570686d0',
                'certificate' : './azure.pem'
            }
        )

    def test_connect(self):
        """ this tests that a the correct region endpoint
        in returned by the connect function
        """

        ctx = self.get_mock_context('test_connect')
        current_ctx.set(ctx=ctx)

        azure_client = connection.AzureConnectionClient().client()
        subscription = azure_client.get_subscription()
        self.assertTrue(type(azure_client), ServiceManagementService)
        self.assertEqual(subscription.subscription_id,
                         ctx['subscription'])