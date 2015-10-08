### Author: HIROSE Masaaki <hirose31 _at_ gmail.com>

global mysql_options
mysql_options = os.getenv('DSTAT_MYSQL') or ''

global target_status
global _basic_status
global _extra_status
_basic_status = (
    ('Queries'                       , 'qps'),
    ('Com_select'                    , 'sel/s'),
    ('Com_insert'                    , 'ins/s'),
    ('Com_update'                    , 'upd/s'),
    ('Com_delete'                    , 'del/s'),

    ('Connections'                   , 'con/s'),
    ('Threads_connected'             , 'thcon'),
    ('Threads_running'               , 'thrun'),
    ('Slow_queries'                  , 'slow'),
    )
_extra_status = (
    ('Innodb_rows_read'              , 'r#read'),
    ('Innodb_rows_inserted'          , 'r#ins'),
    ('Innodb_rows_updated'           , 'r#upd'),
    ('Innodb_rows_deleted'           , 'r#del'),

    ('Innodb_data_reads'               , 'rdphy'),
    ('Innodb_buffer_pool_read_requests', 'rdlgc'),
    ('Innodb_data_writes'              , 'wrdat'),
    ('Innodb_log_writes'               , 'wrlog'),

    ('innodb_buffer_pool_pages_dirty_pct', '%dirty'),
    )

global calculating_status
calculating_status = (
    'Innodb_buffer_pool_pages_total',
    'Innodb_buffer_pool_pages_dirty',
    )

global gauge
gauge = {
    'Slow_queries'                    : 1,
    'Threads_connected'               : 1,
    'Threads_running'                 : 1,
    }


class dstat_plugin(dstat):
    """
    mysql5-innodb, mysql5-innodb-basic, mysql5-innodb-extra

    display various metircs on MySQL5 and InnoDB.
    """
    def __init__(self):
        class pymysqllib(object):
            def __init__(self):
                self.conn = None

            def connect(self):
                if op.debug:
                    print 'mysql5_innodb using pymysql'
                try:
                    with open(os.path.expanduser("~/.my.cnf")) as dfile:
                        try:
                            import configparser
                        except ImportError:
                            import ConfigParser as configparser
                        parser = configparser.ConfigParser()
                        parser.readfp(dfile)
			args = {}
                        for k,v in parser.items('client'):
                            args[k] = v
                except IOError as e:
                    import errno
                    if e.errno != errno.ENOENT:
                        raise e
                    args = {}
                self.conn = pymysql.connect(**args)

            def reconnect(self):
                self.conn = None
                self.connect()

            def execute(self, cmd):
                cursor = self.conn.cursor()
                cursor.execute(cmd)
                while True:
                    result = cursor.fetchone()
                    if result is None:
                        break
                    yield result

        class mysqlcmd(object):
            def connect(self):
                mysql_candidate = ('/usr/bin/mysql', '/usr/local/bin/mysql')
                mysql_cmd = ''

                for mc in mysql_candidate:
                    if os.access(mc, os.X_OK):
                        mysql_cmd = mc
                        break

                if mysql_cmd:
                    if op.debug:
                        print 'mysql5_innodb using %s' % mysql_cmd
                    try:
                        self.stdin, self.stdout, self.stderr = dpopen('%s -n %s' % (mysql_cmd, mysql_options))
                    except IOError:
                        raise Exception, 'Cannot interface with MySQL binary'
                    return True
                raise Exception, 'Needs MySQL binary'

            def reconnect(self):
                # XXX: This is never reached if mysql tries to exit.
                #      That's because dpopen and readpipe aren't set
                #      up to restart the program if it fails.
                self.stdin.close()
                self.stdout.close()
                self.stderr.close()
		self.connect()

            def execute(self, cmd):
                try:
                    self.stdin.write('{};\n'.format(cmd))
                    for line in readpipe(self.stdout):
                        if line == '':
                            break
                        s = line.split()
                        yield s
                except IOError as e:
                    if op.debug > 1:
                        print '%s: lost pipe to mysql, %s' % (self.filename, e)
                    raise


        self.name = 'MySQL5 InnoDB '
        self.type = 'd'
        self.width = 5
        self.scale = 1000
        try:
            import pymysql
            self.mysqllib = pymysqllib()
        except ImportError:
            self.mysqllib = mysqlcmd()

    def check(self):
        if self.filename.find("basic") >= 0:
            target_status = _basic_status
            self.name += 'basic'
        elif self.filename.find("extra") >= 0:
            target_status = _extra_status
            self.name += 'extra'
        elif self.filename.find("full") >= 0:
            target_status = _basic_status + _extra_status
            self.name += 'full'
        else:
            target_status = _basic_status + _extra_status
            self.name += 'full'

        self.vars = tuple( map((lambda e: e[0]), target_status) )
        self.nick = tuple( map((lambda e: e[1]), target_status) )

        self.mysqllib.connect()


    def extract(self):
        try:
            for s in self.mysqllib.execute('show global status'):
                if s[0] in self.vars:
                    self.set2[s[0]] = float(s[1])
                elif s[0] in calculating_status:
                    self.set2[s[0]] = float(s[1])

            for k in self.vars:
                if k in gauge:
                    self.val[k] = self.set2[k]
                elif k == 'innodb_buffer_pool_pages_dirty_pct':
                    self.val[k] = self.set2['Innodb_buffer_pool_pages_dirty'] / self.set2['Innodb_buffer_pool_pages_total'] * 100
                else:
                    self.val[k] = (self.set2[k] - self.set1[k]) * 1.0 / elapsed

            if step == op.delay:
                self.set1.update(self.set2)

        except Exception, e:
            if op.debug > 1: print '%s: exception %s' % (self.filename, e)
            # try to reconnect
            self.mysqllib.reconnect()
            for name in self.vars: self.val[name] = -1
