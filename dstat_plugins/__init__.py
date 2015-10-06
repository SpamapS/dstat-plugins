import shutil
import sys

import pkg_resources as pr

def install():
    destdir = sys.argv[1]
    datadir = pr.resource_filename(__name__, 'plugins/dstat_mysql5_innodb.py')
    shutil.copytree(datadir, destdir)
