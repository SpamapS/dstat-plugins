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

import subprocess

from dstat_plugins.tests import base


class TestDstatplugins(base.TestCase):

    def test_mysql_innodb(self):
        subprocess.check_call(['dstat','--plugin-name', 'mysql5-innodb', '1',
                               '1'])
