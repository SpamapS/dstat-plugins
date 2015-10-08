#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import glob
import os
import os.path
import shutil
import sys

import pkg_resources as pr


def install():
    destdir = sys.argv[1]
    datadir = pr.resource_filename('dstat_plugins', 'plugins')
    try:
        os.makedirs(destdir)
    except OSError:
        if not os.path.isdir(destdir):
            sys.stderr.write("{} could not be created and does not "
                             "exist.\n".format(destdir))
            sys.exit(1)
    for plugin in glob.glob(os.path.join(datadir, 'dstat_*')):
        shutil.copy(plugin, destdir)
