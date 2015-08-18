import testtools
import time
import test_utils

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import nic

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

TIME_DELAY = 20

class TestInstance(testtools.TestCase):

    def setUp(self):
        super(TestInstance, self).setUp()


    def tearDown(self):
        super(TestInstance, self).tearDown()
        time.sleep(TIME_DELAY)


    def test_create_nic(self):
        ctx = test_utils.mock_ctx('testcreatenic')

        ctx.logger.info("BEGIN create NIC test")

        ctx.logger.info("create NIC")
        current_ctx.set(ctx=ctx)
        nic.create(ctx=ctx)

        ctx.logger.info("check if NIC is release")
            
        nic_machine_id = None
        while nic_machine_id is None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(
                                ctx=ctx
                            )
            time.sleep(TIME_DELAY)
    
        """
        ctx.logger.info("check NIC status")
        status_nic = constants.CREATING
        while status_nic == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_nic = #instance.get_vm_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)    
        
        ctx.logger.info("check VM creation success")
        current_ctx.set(ctx=ctx)
        self.assertEqual(constants.SUCCEEDED, status_vm)

        ctx.logger.info("delete VM")
        current_ctx.set(ctx=ctx)
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("check if NIC is release")
        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None :
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(ctx=ctx)
            time.sleep(TIME_DELAY)
        ctx.logger.info("END create VM test")
        """
    def test_delete_nic(self):
        ctx = test_utils.mock_ctx('testdeletenic')
