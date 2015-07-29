import testtools

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import instance

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.decorators import operation

TEST_LINUX_IMAGE_ID = \
    'b39f27a8b8c64d52b05eac6a62ebad85__\
    Ubuntu-14_10-amd64-server-20150723-en-us-30GB'
SUBSCRIPTION = '3121df85-fac7-48ec-bd49-08c2570686d0'

class TestInstance(testtools.TestCase):

    def mock_ctx(self):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription': SUBSCRIPTION,
            'certificate' : './azure.pem',
            'name': 'TEST_LINUX',
            'image_id': TEST_LINUX_IMAGE_ID,
            'storage_account_url': 'https://pythonstorage.blob.core.windows.net/pythonlinuxvhd/test_linux.vhd',
            'cloud_service': 'linuxPythonTest'
        }

        ctx = MockCloudifyContext(
            properties=test_properties,
            operation=operation
        )

        return ctx

    def test_create_instance(self):
        ctx = self.mock_ctx()
        current_ctx.set(ctx=ctx)
        self.assertEqual('Deploying', instance.run_instances(ctx=ctx))
