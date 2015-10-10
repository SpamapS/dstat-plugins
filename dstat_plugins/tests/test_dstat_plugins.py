# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_dstatplugins
----------------------------------

Tests for `dstat_plugins` module.
"""

import os
import subprocess
import tempfile
import time

from dstat_plugins.tests import base


class TestDstatplugins(base.TestCase):

    def _run_plugin(self, args):
        self.temp_fd, self.temp_path = tempfile.mkstemp()
        d = subprocess.Popen(['dstat', '--debug', '--debug', '-c',
                              '--output', self.temp_path,
                              '--nocolor'] + args)
        time.sleep(1)
        d.terminate()
        return d.wait()

    def test_mysql_innodb(self):
        self.assertEqual(-15, self._run_plugin(['--mysql5-innodb', '1', '1']))
        csv = os.fdopen(self.temp_fd).read()
        self.assertIn('--mysql5-innodb', csv)

    def test_openstack_rabbitmq(self):
        self.assertEqual(-15, self._run_plugin(
            ['--openstack-rabbitmq', '1', '1']))
        csv = os.fdopen(self.temp_fd).read()
        self.assertIn('novaq', csv)
        self.assertIn('cinderq', csv)
        self.assertIn('otherq', csv)
