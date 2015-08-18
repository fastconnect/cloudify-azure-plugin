import testtools
import time
import test_utils

from plugin import utils
from plugin import constants
from plugin import connection
from plugin import instance

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

TIME_DELAY = 20

class TestInstance(testtools.TestCase):

    def setUp(self):
        super(TestInstance, self).setUp()


    def tearDown(self):
        super(TestInstance, self).tearDown()
        time.sleep(TIME_DELAY)

    def test_create(self):
        ctx = test_utils.mock_ctx('testcreate')
        ctx.logger.info("BEGIN create VM test")

        ctx.logger.info("create VM")    
        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx) 
        
        ctx.logger.info("check VM status")
        current_ctx.set(ctx=ctx)
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            status_vm = instance.get_vm_provisioning_state(ctx=ctx)
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


    def test_delete(self):    
        ctx = test_utils.mock_ctx('testdelete')
        ctx.logger.info("BEGIN delete VM test")
    
        ctx.logger.info("create VM")    
        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx) 

        ctx.logger.info("check VM status")
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_vm_provisioning_state(ctx=ctx)
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check VM creation success")
        current_ctx.set(ctx=ctx)
        self.assertEqual( constants.SUCCEEDED, status_vm)
        
        ctx.logger.info("delete VM")
        current_ctx.set(ctx=ctx)
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("check if NIC is release")
        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(
                                    ctx=ctx
                                )

            time.sleep(TIME_DELAY)
        ctx.logger.info("END delete VM test")


    def test_conflict(self):
        ctx = test_utils.mock_ctx('testconflict')

        ctx.logger.info("BEGIN conflict VM test")

        ctx.logger.info("create VM")
        current_ctx.set(ctx=ctx)
        instance.create(ctx=ctx)
        
        ctx.logger.info("check VM creation success")
        status_vm = constants.CREATING
        while status_vm == constants.CREATING :
            current_ctx.set(ctx=ctx)
            status_vm = instance.get_vm_provisioning_state(
                            ctx=ctx
                        )
            time.sleep(TIME_DELAY)

        ctx.logger.info("VM creation conflict")
        current_ctx.set(ctx=ctx)
        self.assertRaises(utils.WindowsAzureError,
                         instance.create,
                         ctx=ctx
                         )

        ctx.logger.info("delete VM")
        current_ctx.set(ctx=ctx)
        self.assertEqual(202, instance.delete(ctx=ctx))

        ctx.logger.info("check if NIC is release")
        nic_machine_id = "nicmachineName"
        while nic_machine_id is not None:
            current_ctx.set(ctx=ctx)
            nic_machine_id = instance.get_nic_virtual_machine_id(
                                ctx=ctx
                            )
            time.sleep(TIME_DELAY)
        
        ctx.logger.info("check vm provisionning state in a deleted machine")
        current_ctx.set(ctx=ctx)
        self.assertRaises(
                          utils.WindowsAzureError,
                          instance.get_vm_provisioning_state,
                          ctx=ctx
                          )

        ctx.logger.info("delete VM conflict")        
        current_ctx.set(ctx=ctx) 
        self.assertEqual(204, instance.delete(ctx=ctx))
        ctx.logger.info("END conflict VM test")
  
     
    def test_stop(self):
        ctx = test_utils.mock_ctx('teststop')
        current_ctx.set(ctx=ctx)
