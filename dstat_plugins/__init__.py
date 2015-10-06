import glob
import shutil
import sys
import os
import os.path

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
