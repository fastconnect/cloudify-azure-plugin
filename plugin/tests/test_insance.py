import testtools

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import instance

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

TEST_LINUX_IMAGE_ID = \
    'b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_2_LTS-amd64-server-20150309-en-us-30GB'
SUBSCRIPTION = '3121df85-fac7-48ec-bd49-08c2570686d0'

class TestInstance(testtools.TestCase):

    def mock_ctx(self):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription': SUBSCRIPTION,
            'certificate' : './azure.pem',
            'name': 'testLinuxPython',
            'image_id': TEST_LINUX_IMAGE_ID,
            'storage_account_url': 'https://pythonstorage.blob.core.windows.net/pythonlinuxvhd/test_linux.vhd',
            'cloud_service': 'linuxPythonTest'
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)


    def test_start(self):
        ctx = self.mock_ctx()
        current_ctx.set(ctx=ctx)
        self.assertEqual('Deploying', instance.start(ctx=ctx))

    def test_conflict(self):
        ctx = self.mock_ctx()
        current_ctx.set(ctx=ctx)
        self.assertRaises(NonRecoverableError, instance.start, ctx=ctx)
