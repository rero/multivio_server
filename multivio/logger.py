#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser
import urllib
import cgi
import re
import json
import datetime

# third party modules
from application import Application


# local modules
class LoggerError:
    class InvalidJsonFormat(Exception):
        pass
    class InvalidLogFile(Exception):
        pass

class LoggerApp(Application):
    def __init__(self, file_name):
        Application.__init__(self)
        try:
            self._file = file(file_name, "a")
        except Exception:
            raise  LoggerError.InvalidLogFile("Cannot open file for writing %s" % file_name)
        self.usage = """Using the POST method it put a log message in the server.<br>"""
    
    def post(self, environ, start_response):
        (path, opts) = self.getParams(environ)
        content = self.getPostForm(environ)
        json_body = content.value
        now = datetime.datetime.today()
        header = '%s - - [%s] "POST %s/%s %s"'\
            % (environ.get('SERVER_NAME'),
            now, path, opts, environ.get('SERVER_PROTOCOL')
            )
        self.addLog(header, json_body)
        start_response('200 OK', [('content-type', 'text/html')])
        return ["Ok"]

    def addLog(self, header, json_body):
        content = json_body #json.loads(json_body)
        self._file.write(header+"\n")
        self._file.write(json.dumps(content, sort_keys=True, indent=4)+"\n")
        self._file.flush()


application = LoggerApp('/tmp/multivio.log')

#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")
    from wsgiref.simple_server import make_server
    server = make_server('', options.port, application)
    server.serve_forever()


