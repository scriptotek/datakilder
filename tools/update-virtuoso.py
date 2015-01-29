from __future__ import print_function
import sys
import subprocess
import tempfile
import ConfigParser

config_file = '../config.ini'


class ISQLWrapper(object):

    def __init__(self, config):
        self.path = config.get('isql', 'path')
        self.hostname = config.get('isql', 'host')
        self.username = config.get('isql', 'user')
        self.password = config.get('isql', 'pass')

    def execute_script(self, script):
        cmd = [self.path, self.hostname, self.username, self.password, script]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        if err:
            raise Exception(err)

        return out

    def execute_cmd(self, cmd):
        if not cmd.endswith(";"):
            cmd = "%s;" % cmd
        # print(">>%s" % cmd)

        tf_query = tempfile.NamedTemporaryFile()
        tf_query.write(cmd)
        tf_query.flush()
        result = self.execute_script(tf_query.name)
        tf_query.close()
        return result


cmds = [
    "SPARQL CLEAR GRAPH <http://data.ub.uio.no/{vocabulary}>",
    "DB.DBA.TTLP_MT (file_to_string_output ('{dir}/{vocabulary}.ttl'), '', 'http://data.ub.uio.no/{vocabulary}')"
]

config = ConfigParser.ConfigParser()
config.readfp(open(config_file, 'r'))

dir = sys.argv[1]
voc = sys.argv[2]
fargs = {'vocabulary': voc, 'dir': dir}

print('Vocabulary: {vocabulary}'.format(**fargs))

isql = ISQLWrapper(config)

for cmd in cmds:
    isql.execute_cmd(cmd.format(**fargs))
