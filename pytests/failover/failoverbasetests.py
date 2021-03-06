from TestInput import TestInputSingleton
from basetestcase import BaseTestCase
from membase.helper.cluster_helper import ClusterOperationHelper
from membase.api.rest_client import RestConnection, RestHelper
from couchbase.documentgenerator import BlobGenerator
from remote.remote_util import RemoteMachineShellConnection, RemoteUtilHelper

class FailoverBaseTest(BaseTestCase):

    @staticmethod
    def setUp(self):
        self._cleanup_nodes = []
        self._failed_nodes = []
        super(FailoverBaseTest, self).setUp()
        self.bidirectional = self.input.param("bidirectional", False)
        self._value_size = self.input.param("value_size", 256)
        self.dgm_run = self.input.param("dgm_run", True)
        credentials = self.input.membase_settings
        self.add_back_flag = False
        self.during_ops = self.input.param("during_ops", None)
        self.graceful = self.input.param("graceful", False)

        self.log.info("==============  FailoverBaseTest setup was finished for test #{0} {1} =============="\
                      .format(self.case_number, self._testMethodName))
        self.gen_create = BlobGenerator('loadOne', 'loadOne_', self._value_size, end=self.num_items)

    @staticmethod
    def tearDown(self):
        if hasattr(self, '_resultForDoCleanups') and len(self._resultForDoCleanups.failures) > 0 \
                    and 'stop-on-failure' in TestInputSingleton.input.test_params and \
                    str(TestInputSingleton.input.test_params['stop-on-failure']).lower() == 'true':
                    # supported starting with python2.7
                    log.warn("CLEANUP WAS SKIPPED")
                    self.cluster.shutdown(force=True)
                    self._log_finish(self)
        else:
            try:
                self.log.info("==============  tearDown was started for test #{0} {1} =============="\
                              .format(self.case_number, self._testMethodName))
                RemoteUtilHelper.common_basic_setup(self.servers)
                self.log.info("10 seconds delay to wait for membase-server to start")
                self.sleep(10)
                for server in self._cleanup_nodes:
                    shell = RemoteMachineShellConnection(server)
                    o, r = shell.execute_command("iptables -F")
                    shell.log_command_output(o, r)
                    o, r = shell.execute_command("/sbin/iptables -A INPUT -p tcp -i eth0 --dport 1000:65535 -j ACCEPT")
                    shell.log_command_output(o, r)
                    o, r = shell.execute_command("/sbin/iptables -A OUTPUT -p tcp -o eth0 --dport 1000:65535 -j ACCEPT")
                    shell.log_command_output(o, r)
                    o, r = shell.execute_command("/etc/init.d/couchbase-server start")
                    shell.log_command_output(o, r)
                    shell.disconnect()
                self.log.info("==============  tearDown was finished for test #{0} {1} =============="\
                              .format(self.case_number, self._testMethodName))
            finally:
                super(FailoverBaseTest, self).tearDown()


