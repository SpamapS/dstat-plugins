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

    def test_mysql_innodb(self):
        tfd, tfpath = tempfile.mkstemp()
        d = subprocess.Popen(['dstat', '--output', tfpath, '--nocolor',
                              '--mysql5-innodb', '1', '1'])
        time.sleep(1)
        d.terminate()
        result = d.wait()
        self.assertEqual(-15, result)
        csv = os.fdopen(tfd).read()
        self.assertIn(
            '"qps","sel/s","ins/s","upd/s","del/s","con/s","thcon","thrun"'
            ',"slow","r#read","r#ins","r#upd","r#del","rdphy","rdlgc"'
            ',"wrdat","wrlog","%dirty"\n', csv)
