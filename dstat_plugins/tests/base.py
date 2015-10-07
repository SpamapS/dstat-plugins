# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
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

import os
import subprocess

import fixtures
import testtools
import testresources


class PluginHome(testresources.TestResourceManager):
    def make(self, dependency_resources):
        self.nt = fixtures.NestedTempfile()
        self.nt.setUp()
        self.testhome = fixtures.TempHomeDir()
        self.testhome.setUp()
        self.path = os.path.join(self.testhome.path, '.dstat')
        subprocess.check_call(['install-dstat-plugins', self.path])

    def clean(self, resource):
        self.testhome.cleanUp()
        self.nt.cleanUp()


class TestCase(testtools.TestCase, testresources.ResourcedTestCase):

    resources = [("plugin_home", PluginHome())]

    """Test case base class for all unit tests."""
