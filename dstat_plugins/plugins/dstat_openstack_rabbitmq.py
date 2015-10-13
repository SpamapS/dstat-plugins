# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

global urllib2
import urllib2

global json
import json

global base64
import base64

global httplib
import httplib

global socket
import socket

global DSTAT_RABBITMQ_API
DSTAT_RABBITMQ_API = os.environ.get('DSTAT_RABBITMQ_API',
                                    '127.0.0.1:15672')
global DSTAT_RABBITMQ_API_USER
DSTAT_RABBITMQ_API_USER = os.environ.get('DSTAT_RABBITMQ_USER',
                                    'guest')
global DSTAT_RABBITMQ_API_PASS
DSTAT_RABBITMQ_API_PASS = os.environ.get('DSTAT_RABBITMQ_PASS',
                                    'guest')

class dstat_plugin(dstat):
    """
    openstack-rabbitmq

    display queue length and rate for openstack queues
    """
    def __init__(self):
        self.types = ['d', 'd']
        self.cols = 2
        scale = 1
        self.vars = ["novaq", "cinderq", "notifq", "otherq"]
        self.name = self.vars
        self.nick = ["qlen", "qpub"]

        self.conn = None
        self.auth = base64.encodestring('%s:%s' % (DSTAT_RABBITMQ_API_USER,
                                                   DSTAT_RABBITMQ_API_PASS))
        self.auth = self.auth.replace('\n', '')
        self.auth = {'Authorization': 'Basic %s' % self.auth}

    def _connect(self):
        try:
            self.conn = httplib.HTTPConnection(DSTAT_RABBITMQ_API)
        except Exception as e:
            if op.debug:
                print "Failed to connect to %s (%s)" % (DSTAT_RABBITMQ_API, e)

    def _extract_fail(self):
        for x in self.vars:
            self.val[x] = (-1, -1.0)

    def extract(self):
        if self.conn is None:
            self._connect()
        if self.conn is None:
            self._extract_fail()
            return
        try:
            self.conn.request('GET', '/api/queues', headers=self.auth)
            content = self.conn.getresponse().read()
        except (socket.error, httplib.HTTPException) as e:
            if op.debug:
                print str(e)
            self._extract_fail()
            return

        content = json.loads(content)
        if not isinstance(content, list):
            self._extract_fail()
            return
        newvals = {}
        for q in content:
            if not isinstance(q, dict):
                continue
            if "name" not in q or "messages" not in q:
                continue
            qname = q["name"]
            if qname.startswith("conductor"):
                target = "novaq"
            elif qname.startswith("scheduler"):
                target = "novaq"
            elif qname.startswith("compute"):
                target = "novaq"
            elif qname.startswith("cinder"):
                target = "cinderq"
            elif qname.startswith("notification"):
                target = "notifq"
            else:
                target = "otherq"
            if "message_stats" not in q:
                if op.debug > 3:
                    print "osmq: no message_stats for %s" % (qname,)
            newval = q["messages"]
            if newval and op.debug > 2:
                print "osmq: len %s -> %s += %d" % (qname, target, newval)
            if "message_stats" in q and "publish" in q["message_stats"]:
                newpub = q["message_stats"]["publish"]
            else:
                newpub = 0
            if newpub and op.debug > 2:
                print "osmq: pub %s -> %s += %d" % (qname, target, newpub)
            if target in newvals:
                newvals[target][0] += newval
                newvals[target][1] += newpub
            else:
                newvals[target] = [newval, newpub]
        if op.debug > 2:
            print "osmq: set1=%s" % (self.set1)
            print "osmq: set2=%s" % (self.set2)
        for target, newval in newvals.items():
            for x in (0, 1):
                if op.debug > 1 and newval[x] != self.set1[target][x]:
                    print "osmq: DELTA target=%s x=%d old=%d new=%d" % (
                        target, x, self.set1[target][x], newval[x])
                if op.debug and self.set1[target] is self.set2[target]:
                    print "osmq: REFERENCE ERROR"
                self.set2[target][x] = newval[x]
                self.val[target][x] = newval[x] - self.set1[target][x]
                if step == op.delay:
                    self.set1[target][x] = newval[x]
