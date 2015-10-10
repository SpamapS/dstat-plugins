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
    rabbitmq-queues

    display queue counts and message totals in RabbitMQ
    """
    def __init__(self):
        self.types = ['d', 'f']
        self.cols = 2
        scale = 1
        self.vars = ["novaq","cinderq","otherq"]
        self.name = self.vars
        self.nick = ["len", "rate"]

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
        for q in content:
            if not isinstance(q, dict):
                continue
            if "name" not in q or "messages" not in q:
                continue
            if q["name"].startswith("conductor"):
                target = "novaq"
            elif q["name"].startswith("scheduler"):
                target = "novaq"
            elif q["name"].startswith("compute"):
                target = "novaq"
            elif q["name"].startswith("cinder"):
                target = "cinderq"
            else:
                target = "otherq"
            self.val[target][0] = q["messages"]
            if "message_stats" in q and "deliver_details" in q["message_stats"]:
                self.val[target][1] = float(
                    q["message_stats"]["deliver_details"]["rate"])
