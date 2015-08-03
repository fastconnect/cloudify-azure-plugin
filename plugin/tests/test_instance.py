import testtools
import time

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import instance

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

from azure import WindowsAzureError

TEST_LINUX_IMAGE_ID = \
    'b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_2_LTS-amd64-server-20150309-en-us-30GB'
SUBSCRIPTION = '3121df85-fac7-48ec-bd49-08c2570686d0'
TIME_DELAY = 30

class TestInstance(testtools.TestCase):

    def mock_ctx(self, test_name):
        """ Creates a mock context for the instance
            tests
        """

        test_properties = {
            'subscription': SUBSCRIPTION,
            'certificate' : './azure.pem',
            'name': test_name,
            'image_id': TEST_LINUX_IMAGE_ID,
            'storage_account': 'pythonstorage',
            'storage_container': 'pythonlinuxvhd',
            'cloud_service': 'linuxPythonTest'
        }

        return MockCloudifyContext(node_id='test',
                                   properties=test_properties)

    def is_os_disk_created(self, ctx):
        current_ctx.set(ctx=ctx)
        blob_service = connection.AzureConnectionClient().storageClient()
        try:
            blob_service.get_blob_properties(
                    ctx.node.properties['storage_container'],
                    '{0}.vhd'.format(ctx.node.properties['name'])
                    )
            return True
        except WindowsAzureError:
            return False


    def setUp(self):
        super(TestInstance, self).setUp()

    def tearDown(self):
        ''' Add delay between tests to perform tests on Azure'''
        super(TestInstance, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_start(self):
        ctx = self.mock_ctx('teststart')
        current_ctx.set(ctx=ctx)
        self.assertEqual('Running', instance.start(ctx=ctx))
        while not self.is_os_disk_created(ctx) :
            print 'Waited for os disk creation'
            time.sleep(10)
        instance.stop(ctx=ctx)

    def test_conflict(self):
        ctx = self.mock_ctx('testconflict')
        current_ctx.set(ctx=ctx)
        instance.start(ctx=ctx)
        time.sleep(TIME_DELAY)
        self.assertRaises(NonRecoverableError, instance.start, ctx=ctx)
        while not self.is_os_disk_created(ctx) :
            print 'Waited for os disk creation'
            time.sleep(10)
        instance.stop(ctx=ctx)

    def test_stop(self):
        ctx = self.mock_ctx('teststop')
        current_ctx.set(ctx=ctx)
        instance.start(ctx=ctx)
        while not self.is_os_disk_created(ctx):
            print 'Waited for os disk creation'
            time.sleep(10)
        self.assertEqual('Succeeded',instance.stop(ctx=ctx))
